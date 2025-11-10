# Databricks notebook source
# MAGIC %md
# MAGIC # DLT Pipeline: Gold Layer - Call Summaries & Analytics
# MAGIC 
# MAGIC This pipeline processes completed calls from the Silver layer and creates:
# MAGIC - Call summaries with key metrics
# MAGIC - Agent performance analytics
# MAGIC - Member interaction history
# MAGIC 
# MAGIC **Deploy as DLT Pipeline Job for batch/continuous execution**
# MAGIC **Runs on a schedule (e.g., hourly) to process completed calls**

# COMMAND ----------
# MAGIC %md
# MAGIC ## Silver to Gold: Call Summaries

# COMMAND ----------
# DBTITLE 1,Call Summaries Table
import dlt
from pyspark.sql.functions import *
from pyspark.sql.window import Window

@dlt.table(
    name="call_summaries",
    comment="Post-call summaries with key metrics and insights",
    table_properties={
        "quality": "gold",
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true"
    }
)
@dlt.expect_or_drop("valid_call_id", "call_id IS NOT NULL")
def call_summaries():
    """
    Aggregate enriched transcripts into call summaries
    Processes calls that have been completed (no new transcripts in last 5 minutes)
    Note: Using read.table() for batch mode to read from Silver layer
    """
    # Read enriched transcripts (batch mode - reads all data from Silver layer)
    enriched_df = spark.read.table("member_analytics.call_center.enriched_transcripts")
    
    # Aggregate call-level metrics
    call_summary = (
        enriched_df
        .groupBy("call_id", "member_id", "member_name", "agent_id", "scenario", "complexity", "channel")
        .agg(
            min("timestamp").alias("call_start_time"),
            max("timestamp").alias("call_end_time"),
            count("*").alias("total_segments"),
            countDistinct("speaker").alias("speakers_count"),
            
            # Sentiment metrics
            sum(when(col("sentiment") == "positive", 1).otherwise(0)).alias("positive_count"),
            sum(when(col("sentiment") == "negative", 1).otherwise(0)).alias("negative_count"),
            sum(when(col("sentiment") == "neutral", 1).otherwise(0)).alias("neutral_count"),
            collect_list("sentiment").alias("sentiment_sequence"),
            
            # Intent metrics
            collect_set("intent_category").alias("intents_detected"),
            countDistinct("intent_category").alias("intent_count"),
            
            # Compliance metrics
            sum(when(col("compliance_flag") != "ok", 1).otherwise(0)).alias("compliance_violations_count"),
            collect_list(when(col("compliance_flag") != "ok", col("compliance_flag")).otherwise(None)).alias("compliance_violations"),
            max(when(col("compliance_severity") == "CRITICAL", 1)
                .when(col("compliance_severity") == "HIGH", 2)
                .otherwise(0)).alias("max_compliance_severity"),
            
            # Transcript content
            concat_ws(" ", collect_list("transcript_segment")).alias("full_transcript"),
            
            # Member info
            max("member_balance").alias("member_balance"),
            max("member_life_stage").alias("member_life_stage"),
            
            # Confidence
            avg("confidence").alias("avg_confidence"),
            min("confidence").alias("min_confidence"),
            max("confidence").alias("max_confidence")
        )
        .withColumn(
            "call_duration_seconds",
            unix_timestamp(col("call_end_time")) - unix_timestamp(col("call_start_time"))
        )
        .withColumn(
            "call_duration_minutes",
            (unix_timestamp(col("call_end_time")) - unix_timestamp(col("call_start_time"))) / 60.0
        )
        .withColumn(
            "overall_sentiment",
            when(col("negative_count") > col("positive_count"), "negative")
            .when(col("positive_count") > col("negative_count"), "positive")
            .otherwise("neutral")
        )
        .withColumn(
            "primary_intent",
            col("intents_detected")[0]
        )
        .withColumn(
            "has_compliance_issues",
            col("compliance_violations_count") > 0
        )
        .withColumn(
            "compliance_severity_level",
            when(col("max_compliance_severity") == 1, "CRITICAL")
            .when(col("max_compliance_severity") == 2, "HIGH")
            .otherwise("LOW")
        )
        .withColumn(
            "call_summary",
            concat(
                lit("Call with "), col("member_name"), lit(" about "), col("scenario"), lit(". "),
                lit("Duration: "), round(col("call_duration_minutes"), 1), lit(" minutes. "),
                lit("Overall sentiment: "), col("overall_sentiment"), lit(". "),
                when(col("has_compliance_issues"), lit("Compliance issues detected. ")).otherwise(lit("")),
                lit("Primary intent: "), col("primary_intent"), lit(".")
            )
        )
        .withColumn("summary_created_at", current_timestamp())
        .withColumn("call_date", to_date(col("call_start_time")))
    )
    
    return call_summary

# COMMAND ----------
# MAGIC %md
# MAGIC ## Agent Performance Analytics

# COMMAND ----------
# DBTITLE 1,Agent Performance Table
@dlt.table(
    name="agent_performance",
    comment="Daily agent performance metrics and KPIs",
    table_properties={
        "quality": "gold",
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true"
    }
)
@dlt.expect_or_drop("valid_agent_id", "agent_id IS NOT NULL")
def agent_performance():
    """
    Aggregate agent performance metrics by day
    Calculates KPIs: avg call duration, sentiment scores, compliance rates, etc.
    Note: Using dlt.read() to reference call_summaries table in the same pipeline
    """
    # Read from call_summaries table (created in same pipeline)
    # Use dlt.read() to establish dependency and ensure proper ordering
    call_summaries_df = dlt.read("call_summaries")
    
    agent_perf = (
        call_summaries_df
        .groupBy("agent_id", "call_date")
        .agg(
            count("*").alias("total_calls"),
            
            # Duration metrics
            avg("call_duration_minutes").alias("avg_call_duration_minutes"),
            min("call_duration_minutes").alias("min_call_duration_minutes"),
            max("call_duration_minutes").alias("max_call_duration_minutes"),
            sum("call_duration_minutes").alias("total_call_time_minutes"),
            
            # Sentiment metrics
            avg("positive_count").alias("avg_positive_segments"),
            avg("negative_count").alias("avg_negative_segments"),
            avg("neutral_count").alias("avg_neutral_segments"),
            sum(when(col("overall_sentiment") == "positive", 1).otherwise(0)).alias("positive_calls"),
            sum(when(col("overall_sentiment") == "negative", 1).otherwise(0)).alias("negative_calls"),
            sum(when(col("overall_sentiment") == "neutral", 1).otherwise(0)).alias("neutral_calls"),
            
            # Compliance metrics
            sum(when(col("has_compliance_issues"), 1).otherwise(0)).alias("calls_with_compliance_issues"),
            sum("compliance_violations_count").alias("total_compliance_violations"),
            avg("compliance_violations_count").alias("avg_compliance_violations_per_call"),
            sum(when(col("compliance_severity_level") == "CRITICAL", 1).otherwise(0)).alias("critical_compliance_issues"),
            sum(when(col("compliance_severity_level") == "HIGH", 1).otherwise(0)).alias("high_compliance_issues"),
            
            # Intent metrics
            countDistinct("primary_intent").alias("unique_intents_handled"),
            collect_set("primary_intent").alias("intents_handled"),
            
            # Scenario metrics
            countDistinct("scenario").alias("unique_scenarios_handled"),
            countDistinct("member_id").alias("unique_members_served"),
            
            # Quality metrics
            avg("avg_confidence").alias("avg_transcript_confidence"),
            min("min_confidence").alias("min_transcript_confidence")
        )
        .withColumn(
            "compliance_rate",
            (col("calls_with_compliance_issues") / col("total_calls")) * 100
        )
        .withColumn(
            "positive_sentiment_rate",
            (col("positive_calls") / col("total_calls")) * 100
        )
        .withColumn(
            "negative_sentiment_rate",
            (col("negative_calls") / col("total_calls")) * 100
        )
        .withColumn(
            "calls_per_hour",
            when(col("total_call_time_minutes") > 0, 
                 (col("total_calls") / (col("total_call_time_minutes") / 60.0))).otherwise(0)
        )
        .withColumn(
            "performance_score",
            (
                (100 - col("compliance_rate")) * 0.4 +  # Lower compliance issues = better (40% weight)
                col("positive_sentiment_rate") * 0.3 +   # Higher positive sentiment = better (30% weight)
                (100 - col("negative_sentiment_rate")) * 0.2 +  # Lower negative sentiment = better (20% weight)
                least(col("avg_transcript_confidence") * 100, lit(100)) * 0.1  # Higher confidence = better (10% weight)
            )
        )
        .withColumn("metrics_calculated_at", current_timestamp())
    )
    
    return agent_perf

# COMMAND ----------
# MAGIC %md
# MAGIC ## Member Interaction History

# COMMAND ----------
# DBTITLE 1,Member Interaction History Table
@dlt.table(
    name="member_interaction_history",
    comment="Historical interaction records for members (populated from completed calls)",
    table_properties={
        "quality": "gold",
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true"
    }
)
@dlt.expect_or_drop("valid_member_id", "member_id IS NOT NULL")
def member_interaction_history():
    """
    Create member interaction history from completed calls
    One record per call with summary information
    Note: Using dlt.read() to reference call_summaries table in the same pipeline
    """
    # Read from call_summaries table (created in same pipeline)
    # Use dlt.read() to establish dependency and ensure proper ordering
    call_summaries_df = dlt.read("call_summaries")
    
    member_history = (
        call_summaries_df
        .select(
            col("call_id").alias("interaction_id"),
            col("member_id"),
            col("member_name"),
            col("call_start_time").alias("interaction_date"),
            col("call_date"),
            lit("call").alias("interaction_type"),
            col("scenario").alias("interaction_topic"),
            col("call_summary").alias("summary"),
            col("channel"),
            col("agent_id"),
            col("overall_sentiment"),
            col("primary_intent"),
            col("has_compliance_issues"),
            col("compliance_severity_level"),
            col("call_duration_minutes"),
            col("total_segments"),
            col("member_balance"),
            col("member_life_stage"),
            col("complexity")
        )
        .withColumn("interaction_created_at", current_timestamp())
    )
    
    return member_history

# COMMAND ----------
# MAGIC %md
# MAGIC ## Daily Call Statistics

# COMMAND ----------
# DBTITLE 1,Daily Call Statistics Table
@dlt.table(
    name="daily_call_statistics",
    comment="Daily aggregated call center statistics",
    table_properties={
        "quality": "gold",
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true"
    }
)
def daily_call_statistics():
    """
    Daily aggregated statistics for the entire call center
    Note: Using dlt.read() to reference call_summaries table in the same pipeline
    """
    # Read from call_summaries table (created in same pipeline)
    # Use dlt.read() to establish dependency and ensure proper ordering
    call_summaries_df = dlt.read("call_summaries")
    
    daily_stats = (
        call_summaries_df
        .groupBy("call_date")
        .agg(
            count("*").alias("total_calls"),
            countDistinct("agent_id").alias("active_agents"),
            countDistinct("member_id").alias("unique_members"),
            
            # Duration metrics
            avg("call_duration_minutes").alias("avg_call_duration_minutes"),
            sum("call_duration_minutes").alias("total_call_time_minutes"),
            
            # Sentiment distribution
            sum(when(col("overall_sentiment") == "positive", 1).otherwise(0)).alias("positive_calls"),
            sum(when(col("overall_sentiment") == "negative", 1).otherwise(0)).alias("negative_calls"),
            sum(when(col("overall_sentiment") == "neutral", 1).otherwise(0)).alias("neutral_calls"),
            
            # Compliance metrics
            sum(when(col("has_compliance_issues"), 1).otherwise(0)).alias("calls_with_compliance_issues"),
            sum("compliance_violations_count").alias("total_compliance_violations"),
            sum(when(col("compliance_severity_level") == "CRITICAL", 1).otherwise(0)).alias("critical_issues"),
            sum(when(col("compliance_severity_level") == "HIGH", 1).otherwise(0)).alias("high_issues"),
            
            # Intent distribution
            countDistinct("primary_intent").alias("unique_intents"),
            collect_set("primary_intent").alias("intents_handled"),
            
            # Scenario distribution
            countDistinct("scenario").alias("unique_scenarios"),
            
            # Complexity distribution
            sum(when(col("complexity") == "high", 1).otherwise(0)).alias("high_complexity_calls"),
            sum(when(col("complexity") == "medium", 1).otherwise(0)).alias("medium_complexity_calls"),
            sum(when(col("complexity") == "low", 1).otherwise(0)).alias("low_complexity_calls")
        )
        .withColumn(
            "positive_sentiment_rate",
            (col("positive_calls") / col("total_calls")) * 100
        )
        .withColumn(
            "compliance_rate",
            (col("calls_with_compliance_issues") / col("total_calls")) * 100
        )
        .withColumn(
            "avg_calls_per_agent",
            col("total_calls") / col("active_agents")
        )
        .withColumn("stats_calculated_at", current_timestamp())
    )
    
    return daily_stats

