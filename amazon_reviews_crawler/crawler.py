#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import json
import logging
import requests
import sys
import argparse


REVIEW_URL = "https://www.amazon.{region}/reviews/{product_id}"
AMAZON_MAPPINGS = {"uk": "co.uk", "us": "com"}


def get_region(region="uk"):
    """Return regional amazon web domain suffix"""
    return AMAZON_MAPPINGS.get(region, region)


def get_review_page(product_id, region="uk", url=None):
    """Request the review page url and return a BeautifulSoup instance"""
    region = get_region(region)
    r = requests.get(url or REVIEW_URL.format(region=region, product_id=product_id))
    if r.ok:
        return BeautifulSoup(r.content, features="lxml")
    raise Exception("unprocessible page")


def extract_review_text(soup, region="uk"):
    """Extract review text information from BeautifulSoup instance"""
    reviews = soup.find_all("span", {"class": "review-text-content"})
    reviews_text = []
    for review in reviews:
        review_text = review.get_text()
        reviews_text.append(review_text)
    link = soup.find("li", {"class": "a-last"})
    if link:
        try:
            region = get_region(region)
            if link.a:
                href = link.a.attrs["href"]
                url = "https://www.amazon.{region}{href}".format(
                    region=region, href=href
                )
                logging.debug("crawling next review page: %s", url)
                next_review = get_review_page(None, region=region, url=url)
                reviews_text.extend(extract_review_text(next_review, region=region))
        except Exception as err:
            logging.debug("error crawling next review page: %s", str(err))
            pass
    return reviews_text


def get_reviews_from_product_id(product_id, region="uk"):
    """Get review text from a product id"""
    try:
        soup = get_review_page(product_id, region=region)
        return extract_review_text(soup, region=region)
    except Exception as err:
        logging.debug("error crawling review page: %s", str(err))
        return []


def get_reviews_from_product_ids(product_ids=[], region="uk"):
    """Get all reviews text from a list of product ids"""
    return [
        {product_id: get_reviews_from_product_id(product_id, region=region)}
        for product_id in product_ids
    ]


def runner():
    """Runner entry point accepting system arguments and extract reviews"""
    parser = argparse.ArgumentParser(description="Add some integers.")
    parser.add_argument("-r", "--region", type=str, default="uk")
    parser.add_argument("-l", "--log", type=str, default="INFO")
    parser.add_argument(
        "product_ids", metavar="N", type=str, nargs="+", help="list of product ids"
    )
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log.upper()))
    reviews_text = get_reviews_from_product_ids(args.product_ids, args.region)
    logging.debug(reviews_text)
    return reviews_text


if __name__ == "__main__":
    reviews_text = runner()
    # you can use this entry point to generate a pretty printed json output.
    # simply run with python crawler.py PRODUCT_IDS... --region uk > out.json
    print(json.dumps(reviews_text, sort_keys=True, indent=2))
