# -*- coding: utf-8 -*-
import hashlib
import requests
import json

IMG_LIST = []


class InstagramScrapy(object):
    def __init__(self):
        self.timeout = 20
        self.session = requests.session()
        self.session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
        self.session.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        self.session.headers["Accept-Encoding"] = "gzip, deflate, br"
        self.session.headers["Accept-Language"] = "zh-CN,zh;q=0.9"
        self.base_url = 'https://www.instagram.com/graphql/query/?query_hash={0}&variables=%7B"id"%3A"{1}"%2C"first"%3A12%2C"after"%3A"{2}"%7D'
        self.uuid = "f2405b236d85e8296cf30347c9f08c2a"

    def start(self, url):
        img_list = []
        # url 是某个ins 博主的链接
        res = self.session.get(url, timeout=self.timeout, verify=False)
        start = res.text.find("window._sharedData = ") + len("window._sharedData = ")
        end = res.text.find(";</script>", start)
        # 从源码中获取sharedata, 从而获得首页图片， ins博主信息， 和 继续请求的参数
        json_info = res.text[start:end]
        json_dict = json.loads(json_info)
        username = json_dict["entry_data"]["ProfilePage"][0]["graphql"]["user"]["username"]
        user_id = json_dict["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
        # 粉丝数
        followers = json_dict["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_followed_by"]["count"]
        # 发帖数量
        artiles = json_dict["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["count"]
        introduction = json_dict["entry_data"]["ProfilePage"][0]["graphql"]["user"]["biography"]
        rhx_gis = json_dict["rhx_gis"]
        img_data = json_dict["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
        self.parse_img(img_data)
        next_page = json_dict["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
        # 标识是否还有下一页的图片
        if next_page:
            end_cursor = json_dict["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
            while end_cursor:
                variables = '{"id":"' + user_id + '","first":12,"after":"' + end_cursor + '"}'
                gis = self.get_x_instagram_gis(rhx_gis + ":" + variables)
                self.session.headers["x-instagram-gis"] = gis
                next_url = self.base_url.format(self.uuid, user_id,end_cursor)
                response = self.session.get(next_url, timeout=self.timeout, verify=False)
                res_dict = json.loads(response.text)
                has_next_page = res_dict["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
                if has_next_page:
                    end_cursor = res_dict["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
                else:
                    end_cursor = ""
                img_data = res_dict["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
                self.parse_img(img_data)
            print(IMG_LIST)
            # 博主所有的图片

    def parse_img(self, data):
        for item in data:
            img_url = item["node"]["display_url"]
            IMG_LIST.append(img_url)


    def get_x_instagram_gis(self, info):
        h = hashlib.md5()
        h.update(info.encode("utf-8"))
        return h.hexdigest()


if __name__ == '__main__':
    ss = InstagramScrapy()
    ss.start("https://www.instagram.com/bluebottle/")