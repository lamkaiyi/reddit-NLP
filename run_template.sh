#!/bin/sh

year=2021
while [ $year -ge 2019 ]; do
    python reddit_crawl.py \
        --subreddit_name stocks \
        --comments 1 \
        --output_file "stocks_${year}.json" \
        --year $year
    year=$((year - 1))
done
