from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from datetime import datetime


# ------------ GETS THE CONTENT OF THE REVIEW ------------

def get_review_content(driver):
    """
    Retrieves the full text of the review
    :param driver: It's the webdriver of the page, currently on the restaurant page
    :return: reviewContent
    """
    try:
        review_content_tag = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "partial_entry"))
        )
        review_content = review_content_tag.text
    except TimeoutException:
        review_content = None
        print("Connection timed out for reviews")

    return review_content


# ------------ GETS THE VISIT DATE ON THE REVIEW ------------

def get_review_visit_date(driver):
    """
    Retrieves the date of the review
    :param driver: It's the webdriver of the page, currently on the restaurant page
    :return: visit date
    """
    try:
        review_date_tag = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "prw_reviews_stay_date_hsx"))
        )

        review_date_content = review_date_tag.text.replace("Date of visit:", "")
        review_date_content = review_date_content.strip()
        review_date = datetime.strptime(review_date_content, "%B %Y")

    except TimeoutException:
        print("Timeout Exception : No visit date found for this review")
        review_date = None

    except ValueError:
        review_date = None

    return review_date


# ------------ GETS THE RATING OF THE RESTAURANT ON TE REVIEW ------------

def get_review_rating(driver):
    """
    Retrieves the review score
    :param driver: It's the webdriver of the page, currently on the restaurant page
    :return: rating
    """
    try:
        review_rating_tag = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "ui_bubble_rating"))
        )
        review_rating = int(review_rating_tag.get_attribute("class")[-2])
        # ui_bubble_rating
    except TimeoutException:
        print("Timeout Exception : No rating found for this review")
        review_rating = None

    return review_rating


# ------------ GETS THE TITLE OF THE REVIEW ------------

def get_review_title(driver):
    """
    Retrieves rhe review title
    :param driver: It's the webdriver of the page, currently on the restaurant page
    :return: review title
    """
    try:
        review_title_tag = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "noQuotes"))
        )
        review_title = review_title_tag.text
    except TimeoutException:
        print("Timeout Exception : No Title Found for review")
        review_title = None

    return review_title


# ------------ GETS ALL THE INFOS ON THE REVIEW ------------

def get_review_infos(driver, restau_id, user_id):
    """
    Retrieves all previous information

    :param driver: It's the webdriver of the page, currently on the restaurant page
    :param restau_id: The id of the restaurant we are currently scraping
    :param user_id: The if of the user who left this review
    :return: review info
    """
    try:
        review = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "review-container"))
        )
    except TimeoutException:
        print("Timeout Exception : Couldn't find reviews for this restaurant")
        return None

    review_visit_date = get_review_visit_date(review)
    review_content = get_review_content(review)
    review_rating = get_review_rating(review)
    review_title = get_review_title(review)

    return {
        "userid": user_id,
        "restauid": restau_id,
        "title": review_title,
        "content": review_content,
        "visitdate": review_visit_date,
        "rating": review_rating
    }
