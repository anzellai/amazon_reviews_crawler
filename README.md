# Amazon Reviews Crawler

## Summary

Simple script to crawl Amazon Reviews text from product ID(s).
If running via terminal, simply pass the list of product ID(s) as argument, and pass the `--region REGION` flag as the Amazon website domain suffix, currently mapping with only "uk" to "co.uk" and "us" to "com". If you pass the region outside of this mapping, the suffix will be used from your input.

If you need to see the runner log, set up environment with, pass the logging flag `--log=DEBUG`.


## Setup

`pip install -r requirements.txt`


## Example

Crawling product ID "ABCDE", and run:

`python amazon_reviews_crawler/crawler.py ABCDE --region uk`
