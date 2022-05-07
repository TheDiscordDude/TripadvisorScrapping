import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from scrapLib import *

if __name__ == "__main__":
    db, cursor = db_connect()
    if len(sys.argv) == 3:
        from_ = int(sys.argv[1])
        to_ = int(sys.argv[2])
        condition = "id between {} and {} and treated=FALSE".format(from_, to_)
        urls = get_column_from_table("url", "linkRestaurants", cursor, conditions=condition, order_by="id", limit=100)
    else:
        urls = get_column_from_table("url", "linkRestaurants", cursor, conditions="treated=FALSE", order_by="id",
                                     limit=1000)

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    all_language_clicked = False

    while len(urls) > 0:
        # We do operations only if the url is a real restaurant

        current_url = urls[0]
        driver.get(current_url)

        review_number = get_restau_number_of_reviews(driver)
        if review_number > 0:
            # By default, the reviews are in a specific language, so we click on "all languages" to get all the reviews
            if click_all_languages(driver):
                print("reviews of all languages are now present")
            else:
                print("Couldn't find the button to display every reviews")

            num_page = get_number_of_review_pages(review_number)
            restau_id = get_restau_id(current_url)
            if num_page > 0:
                current_url = get_last_visited_restaurant_page(current_url, restau_id, cursor)
                driver.get(current_url)

            print(current_url)
            print("restaurant :", restau_id)
            print("reviewNumber : ", review_number)

            if not (restaurant_exists_in_database(restau_id, cursor)) and num_page > 0:
                # We get all the infos on the restaurant
                try:
                    restau_infos = get_restau_infos(driver, current_url)
                except TimeoutException:
                    print("Timeout Exception while trying to get : restauInfos")
                except StaleElementReferenceException:
                    print("StaleElement")
                    restart_program()

                # We then upload all restaurant data
                upload_restau(restau_infos, db, cursor)
                print("added")
            else:
                print("already in database")

            # We go through all the pages and register reviews and users
            for j in range(0, num_page):
                # As some reviews are not entirely displayed, we need to show them entirely.
                try:
                    click_more_button(driver)
                except StaleElementReferenceException:
                    print("Stale exception wile clicking on the 'More' button")
                    restart_program()
                try:
                    users = WebDriverWait(driver, 10).until(
                        ec.presence_of_all_elements_located((By.CLASS_NAME, "member_info"))
                    )
                except TimeoutException:
                    print("Timed out waiting for restaurant page to load")
                    users = []

                for k in range(len(users)):
                    # Sometimes, there is a StaleElementException here, and we need to restart the program
                    try:
                        user_link = get_user_link_from_review(k, driver)
                    except StaleElementReferenceException:
                        print("Stale Exception for User link")
                        restart_program()

                    user_id = None
                    # Tripadvisor sometimes takes reviews from Facebook etc.
                    # So there is no userLink or userId, and we don't want to scrap data
                    # Outside Tripadvisor
                    if user_link:
                        user_id = get_user_id(user_link)
                        print("userId:", user_id)
                    if user_id:
                        # Sometimes there are users that delete their account
                        # This variable tracks this very thing, because we don't
                        # Want reviews that don't belong to anyone
                        user_exists = True

                        # It is of course useless to search data on a user that already exists
                        # In database
                        if user_link and not (user_exists_in_database(user_id, cursor)):
                            driver.execute_script("window.open('');")
                            driver.switch_to.window(driver.window_handles[1])
                            driver.get(user_link)
                            try:
                                user_infos = get_user_infos(driver, user_link)
                            except StaleElementReferenceException:
                                print("Stale Element while getting User Infos")
                                restart_program()
                            # the userInfos are None when the user doesn't exist anymore
                            if not user_infos:
                                user_exists = False
                                print("No data found about this user. His review will not be uploaded")
                            else:
                                upload_user(user_infos, db, cursor)
                                print("added")
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])

                        else:
                            print("already in database")

                        # We upload the review only when a user exists
                        if user_exists:
                            print("review:", user_id, restau_id)
                            try:
                                review_infos, already_exists = get_review_infos(k, driver, restau_id, user_id, cursor)
                            except StaleElementReferenceException:
                                print("Stale Exception while getting Review Infos")
                                restart_program()

                            if already_exists:
                                print("already exists")
                            else:
                                upload_review(review_infos, db, cursor)
                                print("added")

                    else:
                        print("This user doesn't exist anymore, his reviews will not be uploaded")

                # This block of code tries to get to the next page
                # when we arrive at the end, either there is no "Next" button
                # or it's simply disabled.
                # We break the loop when that happens.
                try:
                    # change the page
                    button = driver.find_element(By.CLASS_NAME, 'next')

                    if "disabled" in button.get_attribute("class"):
                        break
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(1)
                    print("Next page")
                except NoSuchElementException:
                    print("No More pages")
                    break

        # We set the status of the page as "treated"
        update_restau_link(urls[0], db, cursor)
        urls.pop(0)
    driver.close()
