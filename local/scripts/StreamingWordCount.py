from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, lower, trim

HOST = "3.91.36.108"   # Reemplaza por la IP de Cloud9
PORT = 8083

spark = SparkSession.builder \
    .appName("StructuredStreamingWordCount") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

lines = spark.readStream \
    .format("socket") \
    .option("host", HOST) \
    .option("port", PORT) \
    .load()

words = lines.select(
    explode(
        split(lines.value, " ")
    ).alias("word")
)

clean_words = words.select(
    trim(lower(words.word)).alias("word")
).filter("word <> ''")

word_counts = clean_words.groupBy("word").count()

query = word_counts.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .trigger(processingTime="10 seconds") \
    .start()

query.awaitTermination()