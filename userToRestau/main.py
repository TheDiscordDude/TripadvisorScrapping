from scrapLib import *
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
import time

if __name__ == "__main__":
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    db, cursor = db_connect()

    users = get_column_from_query("""SELECT u.userid
    from user u join review r on u.userid = r.userid
    where u.userid > (SELECT t.userid from t_last_usr t)
    group by u.userid, u.reviews
    having count(r.reviewid) < 10 and count(r.reviewid) < u.reviews
    order by u.userid;""", cursor)
    try:
        for user_id in users:
            url = "https://www.tripadvisor.com/Profile/{}?tab=reviews".format(user_id)
            print(url)
            driver.get(url)

            try:
                next_button = driver.find_element(By.XPATH, ".//div[@class='bRvfG f u']")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                driver.execute_script("arguments[0].click();", next_button)
            except NoSuchElementException:
                print("There is no more reviews on this page")
            except StaleElementReferenceException:
                print("StaleElementReferenceException while clicking the Show More")
                driver.quit()
                restart_program()

            all_restau_avis = driver.find_elements(By.XPATH, "//span[@class='ui_icon restaurants fuEgg']")
            maxNbReviews = 10

            last_height = 0

            while len(all_restau_avis) < maxNbReviews and last_height != driver.execute_script("return document.body.scrollHeight;"):
                all_restau_avis = driver.find_elements(By.XPATH, "//span[@class='ui_icon restaurants fuEgg']")
                last_height = driver.execute_script("return document.body.scrollHeight;")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.8)

            all_restau_avis = driver.find_elements(By.XPATH, "//span[@class='ui_icon restaurants fuEgg']/ancestor::a")
            print("treating :", user_id, len(all_restau_avis))
            for i in range(len(all_restau_avis)):

                restau_url = all_restau_avis[i].get_attribute('href')
                restau_id = get_restau_id(restau_url)

                id2 = re.findall(r"g[0-9]+", restau_url)[0]
                id2 = int(id2[1:])

                a_tag = driver.find_element(By.XPATH, f"//a[contains(@href,'/ShowUserReviews-g{id2}-d{restau_id}')]")

                review_url = a_tag.get_attribute('href')
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(review_url)
                if not (restaurant_exists_in_database(restau_id, cursor)):
                    try:
                        restau_infos = get_restau_infos(driver, review_url)
                    except TimeoutException:
                        print("TimeoutException while getting restau infos")
                        driver.quit()
                        restart_program()
                    except StaleElementReferenceException:
                        print("StaleElementReferenceException while getting restau infos")
                        driver.quit()
                        restart_program()
                    print("RESTAURANT :", restau_id)
                    print("Uploading restaurant ... ", end="")
                    upload_restau(restau_infos, db, cursor)
                    print("uploaded")
                print("Getting review Date ... ", end="")
                review_visit_date = get_review_visit_date(driver)
                print("Done")
                if not (review_exists_in_database(user_id, restau_id, review_visit_date, cursor)):
                    try:
                        print("Getting review Infos ... ", end="")
                        review_infos = get_review_infos(driver, restau_id, user_id)
                        print("Done")
                    except StaleElementReferenceException:
                        print("StaleElementReferenceException while getting review infos")
                        driver.quit()
                        restart_program()
                    print("reviews:", user_id, restau_id, review_visit_date)
                    if not(review_infos is None):
                        print("Uploading review ... ", end="")
                        upload_review(review_infos, db, cursor)
                        print("uploaded")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            print("Updating last treated user ... ", end="")
            update_last_user(user_id, cursor, db)
            print("updated")
    except StaleElementReferenceException:
        print("Unexpected StaleElementException Somewhere in project")
        driver.quit()
        restart_program()
    except WebDriverException:
        print("WebDriverException somewhere in project")
        driver.quit()
        restart_program()
    driver.quit()
    print("End of program")
    restart_program()
