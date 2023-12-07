#!/usr/bin/env python3
import os
import re
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
import pyautogui


class ScraperX:
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    # options.add_argument('--headless')

    def __init__(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.is_signed_in = False
        self.is_country_selected = False
        self.is_first_upload = True

    def get_product_links(self, url, product_category, num_of_product):
        page_num = 1
        next_page = '?page='
        for i in range(48, num_of_product, 48):
            product_links = {product_category: [product.find_element_by_tag_name('a').get_attribute('href') for product in self.driver.find_elements_by_class_name('product-detail-main')]}
            df = pd.DataFrame.from_dict(product_links)
            # if file does not exist write header
            if not os.path.isfile(product_category + 'links.csv'):
                df.to_csv(product_category + 'links.csv', index=None)
            else:  # else if exists so append without writing the header
                df.to_csv(product_category + 'links.csv', mode='a', header=False, index=None)
            page_num += 1
            self.driver.get(url + next_page + str(page_num))
            sleep(3)

    def get_products(self, url, product_category, num_of_product):
        # actions = ActionChains(self.driver)
        self.driver.get(url)
        sleep(3)
        # self.get_product_links(url=url, product_category=product_category, num_of_product=num_of_product)
        df = pd.read_csv(product_category + "links.csv", index_col=None)
        for index, row in df.iterrows():
            product = {}
            self.driver.get(url=row[product_category])
            sleep(3)
            product_name = self.driver.find_element_by_tag_name('h1').text
            price = self.driver.find_element_by_class_name('pdp--SalePriceLbl').find_elements_by_tag_name('span')[1].text
            price = price[1:]
            try:
                price_per_serving = self.driver.find_element_by_class_name('pdp--priceServeRow').text
                price_per_serving = price_per_serving[2:6]
            except NoSuchElementException:
                price_per_serving = 0
            food_ingredients = self.driver.find_element_by_class_name('food-ingredients')
            food_ingredients_text = food_ingredients.text
            protein_content = re.findall(r'(?<=Protein |protein )(\d.+)g', food_ingredients_text)
            if len(protein_content) > 0:
                protein_content = protein_content[0]
            else: protein_content = 0
            calories = re.findall(r'(\d{1,5})(?=Calories )', food_ingredients_text)
            if len(calories) > 0:
                calories = calories[0]
            else: calories = 0
            serving_size = self.driver.find_elements_by_class_name('productInfoRow')[2].find_element_by_tag_name('p').text
            serving_size = re.findall(r'(\d+)', serving_size)
            if len(serving_size) > 0:
                serving_size = re.sub(r'\D', '', str(serving_size))
            else: serving_size = 0
            servings_per_container = self.driver.find_elements_by_class_name('productInfoRow')[3].find_element_by_tag_name('p').text
            servings_per_container = re.findall(r'(\d+)', servings_per_container)
            if len(servings_per_container) > 0:
                servings_per_container = servings_per_container[0]
            else: servings_per_container = 0
            fat_content = re.findall(r'(.*)g(?=Fat)', food_ingredients_text)
            if len(fat_content) > 0:
                fat_content = fat_content[0]
            else: fat_content = 0
            sugar = re.findall(r'(?<=Sugars )|(?<=Sugars \(less than\) )(\d)', food_ingredients_text)
            if len(sugar) > 0 and str(sugar).lower() != 'nan':
                sugar = sugar[0]
            else: sugar = 0
            vegan = re.findall(r'(?<=Vegan )', food_ingredients_text)
            if len(vegan) > 0:
                vegan = 'Yes'
            else: vegan = 'No'
            product["product_name"] = [product_name]
            product["buy_link"] = [row[product_category]]
            product["protein_content"] = [protein_content]
            product["fat_content"] = [fat_content]
            product["calories"] = [calories]
            product["serving_size"] = [serving_size]
            product["price"] = [price]
            product["servings"] = [servings_per_container]
            product["price_per_serving"] = [price_per_serving]
            product["vegan"] = [vegan]
            product["sugar"] = [sugar]
            df = pd.DataFrame.from_dict(product)
            # if file does not exist write header
            if not os.path.isfile(product_category + '.csv'):
                df.to_csv(product_category + '.csv', index=None)
            else:  # else if exists so append without writing the header
                df.to_csv(product_category + '.csv', mode='a', header=False, index=None)

    def get_preworkout(self, url, product_category, num_of_products):
        self.driver.get(url + product_category)
        sleep(3)
        if not self.is_country_selected:
            self.driver.find_element_by_class_name('Modal-inner').find_element_by_tag_name('button').click()
            self.is_country_selected = True
        for i in range(0, num_of_products, 20):
            product_links = {product_category: [product.get_attribute('href') for product in
                                              self.driver.find_elements_by_class_name('product__name')[i:]]}
            df = pd.DataFrame.from_dict(product_links)
            # if file does not exist write header
            if not os.path.isfile(product_category + 'links.csv'):
                df.to_csv(product_category + 'links.csv', index=None)
            else:  # else if exists so append without writing the header
                df.to_csv(product_category + 'links.csv', mode='a', header=False, index=None)
            load_more_button = self.driver.find_element_by_class_name('lazy-loader')
            self.driver.execute_script('arguments[0].scrollIntoView(true);', load_more_button)
            self.driver.find_element_by_class_name('lazy-loader').click()
            sleep(3)

        df = pd.read_csv(product_category + "links.csv", index_col=None)
        for index, row in df.iterrows():
            product = {}
            self.driver.get(url=row[product_category])
            sleep(3)
            product_name = self.driver.find_element_by_class_name('Product__name').text
            table_text = self.driver.find_element_by_class_name('facts_table').text
            citrulline_malate = re.findall(r'(?<=Citrulline Malate	)(.*)g', table_text)
            if len(citrulline_malate) > 0:
                citrulline_malate = citrulline_malate[0]
            else: citrulline_malate = 0
            beta_alanine = re.findall(r'(?<=Beta-Alanine)(.*)mg|(?<=Beta-Alanine \(as CarnoSyn®\).)(\d)', table_text)
            if len(beta_alanine) > 0:
                beta_alanine = beta_alanine[0]
            else: beta_alanine = 0
            creatine = re.findall(r'(?<=Creatine Nitrate \(NO3-T®\)	)(.*)g|(?<=Creatine HCl \(as CON-CRET®\)	)(.*)g', table_text)
            if len(creatine) > 0:
                creatine = creatine[0]
            else: creatine = 0
            caffeine = re.findall(r'(?<=Caffeine Anhydrous \()(.*)mg|(?<=Natural Caffeine \(from Coffee Bean\))(.*)mg', table_text)
            if len(caffeine) > 0:
                caffeine = caffeine[0]
            else: caffeine = 0
            taurine = re.findall(r'(?<=Taurine	)(.*)g', table_text)
            if len(taurine) > 0:
                taurine = taurine[0]
            else: taurine = 0
            agmatine_sulfate = re.findall(r'(?<=Agmatine Sulfate )(\d)mg', table_text)
            if len(agmatine_sulfate) > 0:
                agmatine_sulfate = agmatine_sulfate[0]
            else: agmatine_sulfate = 0
            arginine = re.findall(r'(?<=Arginine Silicate)(.*\d)g|(?<=Arginine Alpha Ketoglutarate	)(\d*)g', table_text)
            if len(arginine) > 0:
                arginine = arginine[0]
            else: arginine = 0
            betaine = re.findall(r'(?<=Betaine Nitrate \(as NO3-T®\))(.*)mg|(?<=Betaine \(Trimethylglycine\).)(\d.\d)|(?<=Betaine Anhydrous)(.*)mg', table_text)
            if len(betaine) > 0:
                betaine = betaine[0]
            else: proprietary_blend = 0
            proprietary_blend = re.findall(r'(Proprietary Blend)', table_text)
            if len(proprietary_blend) > 0:
                proprietary_blend = 'Yes'
            else: proprietary_blend = 'No'
            product["product_name"] = [product_name]
            product["buy_link"] = [row[product_category]]
            product["citrulline_malate"] = [citrulline_malate]
            product["beta_alanine"] = [beta_alanine]
            product["creatine"] = [creatine]
            product["caffeine"] = [caffeine]
            product["taurine"] = [taurine]
            product["agmatine_sulfate"] = [agmatine_sulfate]
            product["arginine"] = [arginine]
            product["betaine"] = [betaine]
            product["proprietary_blend"] = [proprietary_blend]
            print("Product:", product)
            df = pd.DataFrame.from_dict(product)
            # if file does not exist write header
            if not os.path.isfile(product_category + '.csv'):
                df.to_csv(product_category + '.csv', index=None)
            else:  # else if exists so append without writing the header
                df.to_csv(product_category + '.csv', mode='a', header=False, index=None)

    def upload_products(self, url, product_category):
        self.driver.get(url=url)
        sleep(3)
        if not self.is_signed_in:
            self.driver.find_element_by_id('user_login').send_keys('admin')
            self.driver.find_element_by_id('user_pass').send_keys('Demo@12345!!!')
            self.driver.find_element_by_id('rememberme').click()
            self.driver.find_element_by_id('wp-submit').click()
            sleep(5)
            self.is_signed_in = True
        df = pd.read_csv(product_category + ".csv", index_col=None)
        for index, row in df.iterrows():
            self.driver.get(url=url)
            sleep(1)
            # if index > 0:
            #     self.is_first_upload = False
            pyautogui.press('enter')
            print("Uploading Product: ", index, row['product_name'], row['buy_link'])
            title = self.driver.find_element_by_id('title')
            title.clear()
            title.send_keys(row['product_name'])
            # if not self.is_first_upload:
            #     self.driver.find_element_by_id('edit-slug-buttons').find_element_by_tag_name('button').click()
            #     new_slug = self.driver.find_element_by_id('new-post-slug')
            #     new_slug.clear()
            #     new_slug.send_keys(row['product_name'])
            #     self.driver.find_element_by_id('edit-slug-buttons').find_element_by_tag_name('button').click()
            if product_category == 'protein':
                protein_check = self.driver.find_element_by_id('in-c_categories-3')
                if not protein_check.is_selected():
                    protein_check.click()
            elif product_category == 'preworkout':
                preworkout_check = self.driver.find_element_by_id('in-c_categories-5')
                if not preworkout_check.is_selected():
                    preworkout_check.click()
            else:
                protein_bar_check = self.driver.find_element_by_id('in-c_categories-4')
                if not protein_bar_check.is_selected():
                    protein_bar_check.click()
            buy = self.driver.find_element_by_id('buy-link')
            buy.clear()
            buy.send_keys(str(row['buy_link']))
            protein_content = self.driver.find_element_by_id('protein-content-g')
            protein_content.clear()
            protein_content.send_keys(str(row['protein_content']))
            fat_content = self.driver.find_element_by_id('fat-content-g')
            fat_content.clear()
            fat_content.send_keys(str(row['fat_content']))
            calories = self.driver.find_element_by_id('calories')
            calories.clear()
            calories.send_keys(str(row['calories']))
            serving_size = self.driver.find_element_by_id('serving-size-g')
            serving_size.clear()
            serving_size.send_keys(str(row['serving_size']))
            price = self.driver.find_element_by_id('price-usd')
            price.clear()
            price.send_keys(str(row['price']))
            servings = self.driver.find_element_by_id('servings')
            servings.clear()
            servings.send_keys(str(row['servings']))
            price_per_serving = self.driver.find_element_by_id('price-serving-g')
            price_per_serving.clear()
            price_per_serving.send_keys(str(row['price_per_serving']))
            Select(self.driver.find_element_by_id('vegan')).select_by_visible_text(str(row['vegan']))
            sugar = self.driver.find_element_by_id('sugar-g')
            sugar.clear()
            sugar.send_keys(str(row['sugar']))
            button_publish = self.driver.find_element_by_id('publish')
            actions = ActionChains(self.driver)
            actions.move_to_element(button_publish)
            actions.click(button_publish)
            actions.perform()
            sleep(2)
            print('Product Successfully Uploaded: ', index, row['product_name'], row['buy_link'])

    def finish(self):
        self.driver.close()
        self.driver.quit()


def main():
    # ***************************************************************
    #    The program starts from here
    # ***************************************************************
    upload_url = 'http://suppviz.com/wp-admin/post-new.php?post_type=supplements'
    main_url = 'https://www.vitaminshoppe.com'
    protein = "protein"
    protein_url = "https://www.vitaminshoppe.com/c/protein-powders/N-cp99j4"
    preworkout = "preworkout"
    preworkout_url = "https://www.vitaminshoppe.com/c/pre-workout/N-cp99jb"
    scraperx = ScraperX()
    num_of_products = 100
    # scraperx.get_products(url=protein_url, product_category=protein, num_of_product=num_of_products)
    # scraperx.get_products(url=preworkout_url, product_category=preworkout, num_of_product=num_of_products)
    scraperx.upload_products(url=upload_url, product_category=protein)
    scraperx.upload_products(url=upload_url, product_category=preworkout)
    scraperx.finish()


if __name__ == '__main__':
    main()