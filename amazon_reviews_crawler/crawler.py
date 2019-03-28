#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import argparse
import json
import logging
import requests
import sys


REVIEW_URL = "https://www.amazon.{region}/reviews/{product_id}"
AMAZON_MAPPINGS = {"uk": "co.uk", "us": "com"}


def get_region(region="uk"):
    """Return regional amazon web domain suffix"""
    return AMAZON_MAPPINGS.get(region, region)


def get_review_page(product_id, region="uk", url=None):
    """Request the review page url and return a BeautifulSoup instance"""
    region = get_region(region)
    r = requests.get(
        url or REVIEW_URL.format(region=region, product_id=product_id),
        headers={
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        },
    )
    if r.ok:
        return BeautifulSoup(r.content, features="lxml")
    raise Exception("unprocessible page")


def extract_review_meta(soup, region="uk"):
    """Extract review meta information from BeautifulSoup instance"""
    reviews = soup.find_all("div", {"class": "review"})
    reviews_meta = []
    for review in reviews:
        content = review.find("span", {"class": "review-text-content"})
        review_text = content.get_text().strip()
        review_profile, review_star, review_title = "", "", ""
        try:
            profile = review.find("span", {"class": "a-profile-name"})
            review_profile = profile.get_text().strip()
        except Exception as err:
            logging.debug("error parsing review profile: %s", str(err))
        try:
            star = review.find("a", {"class": "a-link-normal"})
            review_star = star.get_text().strip()
        except Exception as err:
            logging.debug("error parsing review star: %s", str(err))
        try:
            title = review.find("a", {"class": "review-title"})
            review_title = title.get_text().strip()
        except Exception as err:
            logging.debug("error parsing review title: %s", str(err))
        reviews_meta.append(
            {
                "profile": review_profile,
                "star": review_star,
                "title": review_title,
                "text": review_text,
            }
        )

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
                reviews_meta.extend(extract_review_text(next_review, region=region))
        except Exception as err:
            logging.debug("error crawling next review page: %s", str(err))
            pass
    return reviews_meta


def get_reviews_from_product_id(product_id, region="uk"):
    """Get review text from a product id"""
    try:
        soup = get_review_page(product_id, region=region)
        return extract_review_meta(soup, region=region)
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
