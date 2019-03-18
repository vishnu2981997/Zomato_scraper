import time
from lxml import html
from selenium import webdriver
from collections import defaultdict
import json


def handle_basic_info(header_section, data):
    basic_profile_info = defaultdict()

    basic_profile_info["profile_picture_data"] = []
    profile_picture_data = defaultdict()
    profile_picture_data["src"] = header_section[0][0].find(".//img").attrib["src"] if "src" in header_section[0][
        0].find(".//img").attrib else None
    profile_picture_data["alt"] = header_section[0][0].find(".//img").attrib["alt"] if "alt" in header_section[0][
        0].find(".//img").attrib else None
    basic_profile_info["profile_picture_data"].append(profile_picture_data)

    basic_profile_info["user_name_data"] = []
    user_name_data = defaultdict()
    user_name_data["text"] = header_section[0][0].find(".//div[@class=\'user-header-info-middle\']")[0][0].find(
        ".//a").text
    user_name_data["href"] = \
        header_section[0][0].find(".//div[@class=\'user-header-info-middle\']")[0][0].find(".//a").attrib["href"]
    basic_profile_info["user_name_data"].append(user_name_data)

    if header_section[0][0].find(".//div[@class=\'user-header-info-middle\']")[1].find(".//span") is not None:
        basic_profile_info["alternate_name"] = header_section[0][0].find(".//div[@class=\'user-header-info-middle\']")[
            1].find(".//span").text.strip()
        basic_profile_info["location"] = header_section[0][0].find(".//div[@class=\'user-header-info-middle\']")[
            2].text.strip()
        if len(header_section[0][0].find(".//div[@class=\'user-header-info-middle\']")) > 0:
            basic_profile_info["description"] = header_section[0][0].find(".//div[@class=\'user-header-info-middle\']")[
                3].text.strip()
        else:
            basic_profile_info["description"] = None
    else:
        basic_profile_info["alternate_name"] = None
        basic_profile_info["location"] = header_section[0][0].find(".//div[@class=\'user-header-info-middle\']")[
            1].text.strip()
        if len(header_section[0][0].find(".//div[@class=\'user-header-info-middle\']")) > 0:
            basic_profile_info["description"] = header_section[0][0].find(".//div[@class=\'user-header-info-middle\']")[
                2].text.strip()
        else:
            basic_profile_info["description"] = None

    basic_profile_info["foodie_level"] = []
    foodie_level = defaultdict()
    foodie_level["value"] = header_section.xpath("//div[@class='user-stats_ranking']")[0][0].text
    foodie_level["value_description"] = header_section.xpath("//div[@class='user-stats_ranking']")[0][1].text
    foodie_level["next_level_up_point"] = \
        header_section.xpath("//div[@class='ui mini statistics']")[0][0][1].text.split()[0]
    basic_profile_info["foodie_level"].append(foodie_level)

    if len(header_section.xpath("//div[@class='ui mini statistics']")[0]) > 2:
        basic_profile_info["neighbourhoods"] = []
        neighbourhoods = defaultdict()
        neighbourhoods["count"] = header_section.xpath("//div[@class='ui mini statistics']")[0][1][0][0].text.split()[0]
        neighbourhoods["places"] = [i.find(".//a")[0].text.strip() for i in
                                    header_section.xpath(".//ul[@class='pt5 user-expertise-list']")[0] if
                                    i.find(".//a") is not None]
        basic_profile_info["neighbourhoods"].append(neighbourhoods)
    else:
        basic_profile_info["neighbourhoods"] = None

    data["basic_profile_info"].append(basic_profile_info)


def handle_counts_info(counts_section, data):
    counts_info = defaultdict()
    counts_info["reviews"] = counts_section[1].find(".//div[@class=\'ui label\']").text if counts_section[1].find(
        ".//div[@class=\'ui label\']") is not None else '0'
    counts_info["photos"] = counts_section[2].find(".//div[@class=\'ui label\']").text if counts_section[1].find(
        ".//div[@class=\'ui label\']") is not None else '0'
    counts_info["followers"] = counts_section[3].find(".//div[@class=\'ui label\']").text if counts_section[1].find(
        ".//div[@class=\'ui label\']") is not None else '0'
    counts_info["bookmarks"] = counts_section[4].find(".//div[@class=\'ui label\']").text if counts_section[1].find(
        ".//div[@class=\'ui label\']") is not None else '0'
    counts_info["been_there"] = counts_section[5].find(".//div[@class=\'ui label\']").text if counts_section[1].find(
        ".//div[@class=\'ui label\']") is not None else '0'
    data["counts_info"].append(counts_info)


def handle_reviews(driver, url, data):
    # Get page source
    url = url + "/reviews" if url[-1] != "/" else url + "reviews"
    driver.get(url)
    time.sleep(2)
    scroll_to_bottom(driver, 1)
    page = driver.page_source.encode('utf-8')

    # Convert html page source to tree
    tree = html.fromstring(page)

    reviews_body = tree.find(".//div[@class=\'zs-following-list\']")

    for review in reviews_body:
        handle_review(review, data)


def handle_review(review, data):
    review_data = defaultdict()
    review_data["name"] = review.find(".//div[@class=\'item\']")[1][0][1][0].text
    review_data["place"] = review.find(".//div[@class=\'item\']").find(".//span").text
    review_data["time"] = str(review.find(".//time"))
    review_data["datetime"] = review.find(".//time").attrib["datetime"] if "datetime" in review.find(
        ".//time").attrib else None
    review_data["rating"] = review.find(".//div[@class=\'rev-text\']")[0].attrib["aria-label"].split()[1]
    review_data["text"] = review.find(".//div[@class=\'rev-text\']")[0].tail.strip()
    data["reviews"].append(review_data)


def handle_photos(driver, url, data):
    # Get page source
    url = url + "/photos" if url[-1] != "/" else url + "photos"
    driver.get(url)
    time.sleep(2)
    scroll_to_bottom(driver, 2)
    page = driver.page_source.encode('utf-8')

    # Convert html page source to tree
    tree = html.fromstring(page)
    images_body = tree.find(".//div[@class=\'photosContainer mtop0 row zs-following-list\']")

    for image in images_body:
        handle_image_body(image, data)


def handle_image_body(image, data):
    image_data = defaultdict()
    image_data["href"] = image.find(".//img").attrib["src"].split("?")[0]
    data["photos"].append(image_data)


def handle_followers(driver, url, data):
    # Get page source
    url = url + "/network" if url[-1] != "/" else url + "network"
    driver.get(url)
    time.sleep(2)
    scroll_to_bottom(driver, 3)
    page = driver.page_source.encode('utf-8')

    # Convert html page source to tree
    tree = html.fromstring(page)
    followers_body = tree.find(".//div[@class=\'zs-following-list clearfix user-profile-network-tab ui cards\']")
    following_body = tree.find(".//div[@class=\'zs-following-list  clearfix user-profile-network-tab ui cards\']")

    for follower in followers_body:
        handle_follower(follower, data)

    for following in following_body:
        handle_following(following, data)


def handle_follower(follower, data):
    follower_data = defaultdict()
    follower_data["name"] = follower.find(".//div[@class=\'content\']")[0][0][1].find(".//a").text.strip()
    follower_data["img"] = follower.find(".//div[@class=\'content\']")[0][0].find(".//img").attrib["src"]
    follower_data["href"] = follower.find(".//div[@class=\'content\']")[0][0].find(".//a").attrib["href"]
    temp = "".join(i for i in follower.find(".//div[@class=\'content\']")[0][0][1].find(".//span").text if
                   i not in ["\n", "\t", "(", ")"]).strip().split(",")
    if len(temp) == 2:
        follower_data["reviews"] = temp[0].strip().split()[1]
        follower_data["followers"] = temp[1].strip().split()[0]
    else:
        follower_data["reviews"] = temp[0].strip().split()[1]
        follower_data["followers"] = None
    data["followers"].append(follower_data)


def handle_following(following, data):
    following_data = defaultdict()
    following_data["name"] = following.find(".//div[@class=\'content\']")[0][0][1].find(".//a").text.strip()
    following_data["img"] = following.find(".//div[@class=\'content\']")[0][0].find(".//img").attrib["src"]
    following_data["href"] = following.find(".//div[@class=\'content\']")[0][0].find(".//a").attrib["href"]
    temp = "".join(i for i in following.find(".//div[@class=\'content\']")[0][0][1].find(".//span").text if
                   i not in ["\n", "\t", "(", ")"]).strip().split(",")
    if len(temp) == 2:
        following_data["reviews"] = temp[0].strip().split()[1]
        following_data["followers"] = temp[1].strip().split()[0]
    else:
        following_data["reviews"] = temp[0].strip().split()[1]
        following_data["followers"] = None
    data["following"].append(following_data)


def handle_bookmarks(driver, url, data):
    # Get page source
    url = url + "/bookmarks" if url[-1] != "/" else url + "bookmarks"
    driver.get(url)
    time.sleep(2)
    scroll_to_bottom(driver, 4)
    page = driver.page_source.encode('utf-8')

    # Convert html page source to tree
    tree = html.fromstring(page)
    bookmarks_body = tree.find(".//div[@class=\'ui three cards\']")

    for bookmark in bookmarks_body:
        handle_bookmark(bookmark, data)

    if int(data["counts_info"][0]["bookmarks"]) > 9:

        bookmarks_body = tree.find(".//div[@class=\'more-bookmarks hidden-bookmarks-7 hidden\']").find(
            ".//div[@class=\'ui three cards\']")

        for bookmark in bookmarks_body:
            handle_bookmark(bookmark, data)


def handle_bookmark(bookmark, data):
    bookmark_data = defaultdict()
    bookmark_data["name"] = bookmark[1][0].find(".//a").text
    bookmark_data["place"] = bookmark[1][2].find(".//a").text
    bookmark_data["href"] = bookmark.find(".//a").attrib["href"]
    temp = bookmark.find(".//a").attrib["style"]
    if temp[-1] == ")":
        bookmark_data["img"] = temp[temp.index("(") + 2:temp.index(")") - 1]
    else:
        bookmark_data["img"] = temp[temp.index("(") + 2:temp.index(";") - 2]
    data["bookmarks"].append(bookmark_data)


def handle_been_there(driver, url, data):
    # Get page source
    url = url + "/beenthere" if url[-1] != "/" else url + "beenthere"
    driver.get(url)
    time.sleep(2)
    scroll_to_bottom(driver, 5)
    page = driver.page_source.encode('utf-8')

    # Convert html page source to tree
    tree = html.fromstring(page)

    been_there_body = tree.find(".//div[@class=\'zs-following-list pbot0 clearfix user-profile-bookmark-tab\']")

    for cards in been_there_body:
        for item in cards:
            handle_been_there_item(item, data)


def handle_been_there_item(item, data):
    handle_been_there_item = defaultdict()
    handle_been_there_item["name"] = item[1][0].find(".//a").text
    handle_been_there_item["place"] = item[1][2].find(".//a").text
    handle_been_there_item["href"] = item.find(".//a").attrib["href"]
    temp = item.find(".//a").attrib["style"]
    if temp[-1] == ")":
        handle_been_there_item["img"] = temp[temp.index("(") + 2:temp.index(")") - 1]
    else:
        handle_been_there_item["img"] = temp[temp.index("(") + 2:temp.index(";") - 2]
    data["been_there"].append(handle_been_there_item)


def handle_dine_line(tree, data):
    dine_line_body = tree.find(".//div[@class=\'user-food-journey-container\']")
    return


def scroll_to_bottom(driver, option):
    while True:
        if option == 1:
            try:
                load_more_button = driver.find_element_by_xpath("//div[@class=\'bt zs-load-more mtop\']")
                time.sleep(1)
                load_more_button.click()
            except:
                break

        if option == 2:
            try:
                load_more_button = driver.find_element_by_xpath(
                    "//div[@class=\'ui segment col-l-16 tac zs-load-more\']")
                time.sleep(1)
                load_more_button.click()
            except:
                break

        if option == 3:
            try:
                load_more_button = driver.find_element_by_xpath(
                    "//div[@class=\'ui segment col-l-16 tac zs-load-more mbot\']")
                time.sleep(1)
                load_more_button.click()
            except:
                try:
                    load_more_button = driver.find_element_by_xpath(
                        "//div[@class=\'ui segment col-l-16 tac  zs-load-more\']")
                    time.sleep(1)
                    load_more_button.click()
                except:
                    break

        if option == 4:
            try:
                load_more_button = driver.find_element_by_xpath(
                    "//div[@class=\'bt ratings-city-review-show-all unrated-show-all clearfix city-bookmarks city-bookmarks-7\']")
                time.sleep(1)
                load_more_button.click()
            except:
                break

        if option == 5:
            try:
                load_more_button = driver.find_element_by_xpath(
                    "//div[@class=\'ui segment col-l-16 tac zs-load-more\']")
                time.sleep(1)
                load_more_button.click()
            except:
                break


def main():
    """
    main function
    :return: None
    """
    try:
        # SetUp Firefox driver
        options = webdriver.FirefoxOptions()
        options.headless = False
        options.Proxy = None
        fp = webdriver.FirefoxProfile()
        fp.set_preference("http.response.timeout", 400)
        fp.set_preference("dom.max_script_run_time", 240)
        driver = webdriver.Firefox(options=options, firefox_profile=fp)
    except Exception as e:
        print("Error while initializing driver")

    # Get page source
    url = input()  # "https://www.zomato.com/users/thrivikram-balaji-33680802"
    driver.get(url)  # Enter the instagram page url
    page = driver.page_source.encode('utf-8')

    # Convert html page source to tree
    tree = html.fromstring(page)

    data = defaultdict()

    data["basic_profile_info"] = []
    data["counts_info"] = []
    data["dine_line"] = []
    data["reviews"] = []
    data["photos"] = []
    data["followers"] = []
    data["following"] = []
    data["bookmarks"] = []
    data["been_there"] = []

    header_section = tree.find(".//div[@class=\'ui segment\']")
    handle_basic_info(header_section, data)

    counts_section = tree.find(".//div[@class=\'ui vertical fluid menu user-tab-sorting tabs selectors\']")
    handle_counts_info(counts_section, data)

    if int(data["counts_info"][0]["reviews"]) > 0:
        handle_reviews(driver, url, data)
    else:
        data["reviews"] = {"reviews": data["counts_info"][0]["reviews"]}

    if int(data["counts_info"][0]["photos"]) > 0:
        handle_photos(driver, url, data)
    else:
        data["photos"] = {"photos": data["counts_info"][0]["photos"]}

    if int(data["counts_info"][0]["followers"]) > 0:
        handle_followers(driver, url, data)
    else:
        data["followers"] = {"followers": data["counts_info"][0]["followers"]}

    if int(data["counts_info"][0]["bookmarks"]) > 0:
        handle_bookmarks(driver, url, data)
    else:
        data["bookmarks"] = {"bookmarks": data["counts_info"][0]["bookmarks"]}

    if int(data["counts_info"][0]["been_there"]) > 0:
        handle_been_there(driver, url, data)
    else:
        data["been_there"] = {"been_there": data["counts_info"][0]["been_there"]}

    driver.close()

    with open('result_zomato.json', 'w') as fp:
        json.dump(data, fp)


if __name__ == "__main__":
    main()
