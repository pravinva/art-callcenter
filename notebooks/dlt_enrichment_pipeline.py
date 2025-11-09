# Databricks notebook source
# Databricks notebook source
# MAGIC %md
# MAGIC # DLT Pipeline: Call Center Transcript Enrichment
# MAGIC 
# MAGIC This pipeline continuously processes call transcripts from Zerobus and enriches them with:
# MAGIC - Sentiment analysis
# MAGIC - Intent detection
# MAGIC - Compliance checking
# MAGIC 
# MAGIC **Deploy as DLT Pipeline Job for continuous execution**

# COMMAND ----------
# MAGIC %md
# MAGIC ## Bronze to Silver: Enriched Transcripts

# COMMAND ----------
# DBTITLE 1,Enriched Transcripts Table
import dlt
from pyspark.sql.functions import *

@dlt.table(
    name="enriched_transcripts",
    comment="Enriched call transcripts with sentiment, intent, and compliance flags",
    table_properties={
        "quality": "silver",
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true"
    }
)
@dlt.expect_or_drop("valid_timestamp", "timestamp IS NOT NULL")
@dlt.expect_or_drop("valid_speaker", "speaker IN ('agent', 'customer')")
def enriched_transcripts():
    """
    Stream from Zerobus transcripts and enrich with sentiment, intent, and compliance
    Note: Reading directly from Unity Catalog table
    Unity Catalog must be enabled on the cluster for this to work
    """
    return (
        spark.readStream.table("member_analytics.call_center.zerobus_transcripts")
        .withColumn(
            "sentiment",
            when(
                lower(col("transcript_segment")).rlike("thank|appreciate|great|perfect"),
                lit("positive")
            )
            .when(
                lower(col("transcript_segment")).rlike("frustrated|angry|disappointed|terrible"),
                lit("negative")
            )
            .otherwise(lit("neutral"))
        )
        .withColumn(
            "intent_category",
            when(
                lower(col("transcript_segment")).rlike("contribution|cap"),
                lit("contribution_inquiry")
            )
            .when(
                lower(col("transcript_segment")).rlike("withdraw|access|medical"),
                lit("withdrawal_inquiry")
            )
            .when(
                lower(col("transcript_segment")).rlike("insurance|cover"),
                lit("insurance_inquiry")
            )
            .when(
                lower(col("transcript_segment")).rlike("performance|return"),
                lit("performance_inquiry")
            )
            .when(
                lower(col("transcript_segment")).rlike("beneficiary"),
                lit("beneficiary_update")
            )
            .when(
                lower(col("transcript_segment")).rlike("complaint|frustrated"),
                lit("complaint")
            )
            .otherwise(lit("general_inquiry"))
        )
        .withColumn(
            "compliance_flag",
            when(
                lower(col("transcript_segment")).rlike("guarantee|promise") |
                (lower(col("transcript_segment")).rlike("definitely") & 
                 lower(col("transcript_segment")).rlike("return|grow")),
                lit("guarantee_language")
            )
            .when(
                (col("speaker") == "agent") &
                lower(col("transcript_segment")).rlike("should|recommend|best option"),
                lit("personal_advice")
            )
            .when(
                (col("speaker") == "agent") &
                lower(col("transcript_segment")).rlike("balance") &
                ~lower(col("transcript_segment")).rlike("your"),
                lit("privacy_breach")
            )
            .otherwise(lit("ok"))
        )
        .withColumn(
            "compliance_severity",
            when(
                lower(col("transcript_segment")).rlike("guarantee|promise"),
                lit("CRITICAL")
            )
            .when(
                (col("speaker") == "agent") &
                lower(col("transcript_segment")).rlike("should"),
                lit("HIGH")
            )
            .when(
                (col("speaker") == "agent") &
                lower(col("transcript_segment")).rlike("balance"),
                lit("HIGH")
            )
            .otherwise(lit("LOW"))
        )
        .withColumn("enriched_at", current_timestamp())
    )

# COMMAND ----------
# MAGIC %md
# MAGIC ## Silver to Gold: Online Table Refresh
# MAGIC 
# MAGIC Note: Online Tables are created separately via SQL, but this pipeline ensures
# MAGIC the enriched data is always up-to-date for Online Table refresh

