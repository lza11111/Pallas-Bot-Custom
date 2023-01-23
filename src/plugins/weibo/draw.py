import asyncio
import datetime
import httpx
import timeago
import math
import re
import nonebot
from dateutil import parser
from io import BytesIO
from pathlib import Path
from qrcode.image.pil import PilImage
from PIL import Image, ImageFont, ImageDraw
from pilmoji import Pilmoji

from utils import get_cut_str

global_config = nonebot.get_driver().config

"""
TODO
1. 处理图片回复- ok
2. 处理视频 - ok
3. 处理链接
4. 处理评论
"""
font_path = Path(__file__).parent.parent.parent.parent.joinpath("data").joinpath("font")
font_semibold = str(font_path.joinpath("PingFang-Medium.ttf"))
font_bold = str(font_path.joinpath("sarasa-mono-sc-bold.ttf"))
font_vanfont = str(font_path.joinpath("vanfont.ttf"))

class DrawOption:
    """
    图片参数
    """
    spacing: int
    margin: int
    bg_width: int
    bg_color: str

    @property
    def content_width(self):
        return self.bg_width - self.margin * 2

class DefaultDrawOption(DrawOption):
    def __init__(self) -> None:
        super().__init__()
        self.bg_width = 600
        self.margin = 10
        self.spacing = 20
        self.bg_color = "#FFFFFF"

client = httpx.Client()
client.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        ),
        "referer": f"https://weibo.com",
    }
)
client.cookies.update(
    {
        "SUB": global_config.weibo_sub
    }
)

async def create_weibo_image(data, option: DrawOption = DefaultDrawOption()):
    UP_HEIGHT = 60

    bg_y = option.margin
    # 博主信息
    up_top = bg_y
    up_bg = Image.new("RGB", (option.content_width, UP_HEIGHT + option.spacing), option.bg_color)
    draw = ImageDraw.Draw(up_bg)
    bg_y += UP_HEIGHT + option.spacing

    # 博主头像
    face_size = (60, 60)
    face_url = data["user"]["avatar_large"]
    face_get = client.get(face_url).content
    face_bio = BytesIO(face_get)
    face = Image.open(face_bio)
    face.convert("RGB")
    face = face.resize(face_size)
    mask = Image.new("RGBA", face_size, color=(0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, face_size[0] - 1, face_size[1] - 1), fill=(0, 0, 0, 255))
    up_bg.paste(face, (option.margin, option.margin), mask)

    # 博主名字
    name_font = ImageFont.truetype(font_bold, 24)
    draw.text((80, 15), data["user"]["screen_name"], "#000000", name_font)
    # 发布时间
    follower_font = ImageFont.truetype(font_semibold, 22)
    create_at = parser.parse(data["created_at"]).replace(tzinfo=None)
    draw.text(
        (80, 45),
        timeago.format(create_at, datetime.datetime.now(), locale="zh_CN"),
        "#474747",
        follower_font,
    )

    # 正文
    content_top = bg_y
    content, content_url = await draw_content(data, option)
    bg_y += (content.height + option.spacing if content else 0)

    # 图片
    images_top = bg_y
    images = draw_images(data,option)
    bg_y += (images.height + option.spacing if images else 0)
         
    # 回复图片
    replay_images_top = bg_y
    replay_images = draw_replay_image(data, option)
    bg_y += (replay_images.height + option.spacing if replay_images else 0)

    # 视频
    video_top = bg_y
    video = draw_video(data, option)
    bg_y += (video.height + option.spacing if video else 0)

    # 画原博
    retweet_top = bg_y
    retweet, retweet_url = await draw_retweet(data, option)
    bg_y += (retweet.height + option.spacing if retweet else 0) 

    # 画数据
    info_top = bg_y
    info = draw_info(data, option)
    bg_y += (info.height + option.spacing if info else 0) 

    # 最终画布
    weibo = Image.new("RGB", (option.bg_width, bg_y), option.bg_color)

    # 画博主
    weibo.paste(up_bg, (option.margin, up_top))

    # 画正文
    if content:
        weibo.paste(content, (option.margin, content_top))

    # 画图片
    if images:
        weibo.paste(images, (option.margin, images_top))
    
    if replay_images:
        weibo.paste(replay_images, (option.margin, replay_images_top))

    # 画视频
    if video:
        weibo.paste(video, (option.margin, video_top))

    # 画原博
    if retweet:
        weibo.paste(retweet, (option.margin * 2, retweet_top))
    
    if info:
        weibo.paste(info, (option.margin, info_top))

    return weibo, content_url + retweet_url

async def draw_content(data, option: DrawOption):
    content: str | None = None
    if "isLongText" in data and data["isLongText"] == True:
        url = "https://weibo.com/ajax/statuses/longtext?id={}".format(data["id"])
        content = client.get(url).json()['data']['longTextContent']
    content = content if content else data["text_raw"]
    content_url = tcn_extract(content) or []
    content_font = ImageFont.truetype(font_semibold, 24)
    content_cut_str = "\n".join(get_cut_str(content, math.ceil(option.content_width / 14)))
    _, content_text_y = content_font.getsize_multiline(content_cut_str, spacing=15)
    content_bg = Image.new("RGB", (option.content_width, content_text_y + option.spacing), option.bg_color)
    draw = Pilmoji(content_bg)
    draw.text((10, 10), content_cut_str, "#181818", content_font, spacing=15)
    return content_bg, content_url

def draw_images(data, option: DrawOption):
    # 图片
    if "pic_infos" in data:
        pic_list = []
        pic_height_list = []
        for i, pic_key in enumerate(data["pic_infos"]):
            pic_data = data["pic_infos"][pic_key]["large"]
            pic_url = pic_data["url"]
            pic_get = client.get(pic_url).content
            pic_bio = BytesIO(pic_get)
            pic = Image.open(pic_bio)
            pic_height =  math.floor(option.content_width / pic_data["width"] * pic_data["height"])
            pic = pic.resize((option.content_width, pic_height))
            pic_list.append(pic) 
            pic_height_list.append(pic_height)
        pic_bg = Image.new("RGB", (option.content_width, sum(pic_height_list) + len(pic_height_list) * option.spacing), option.bg_color)
        for i, pic in enumerate(pic_list):
            pic_bg.paste(pic, (0, i if i == 0 else sum(pic_height_list[:i]) + i * option.spacing))
        return pic_bg
    return None

def draw_replay_image(data, option: DrawOption):
    if "url_struct" in data:
        pic_list = []
        pic_height_list = []
        for i, url in enumerate(data["url_struct"]):
            if url["url_type"] != 39 or "pic_infos" not in url:
                continue
            for i, pic_key in enumerate(url["pic_infos"]):
                pic_data = url["pic_infos"][pic_key]["large"]
                pic_url = pic_data["url"]
                pic_get = client.get(pic_url).content
                pic_bio = BytesIO(pic_get)
                pic = Image.open(pic_bio)
                pic_height =  math.floor(option.content_width / pic.width * pic.height)
                pic = pic.resize((option.content_width, pic_height))
                pic_list.append(pic) 
                pic_height_list.append(pic_height)
        if len(pic_list) == 0:
            return None
        pic_bg = Image.new("RGB", (option.content_width, sum(pic_height_list) + len(pic_height_list) * option.spacing), option.bg_color)
        for i, pic in enumerate(pic_list):
            pic_bg.paste(pic, (0, i if i == 0 else sum(pic_height_list[:i]) + i * option.spacing))
        return pic_bg
    return None

def draw_video(data, option: DrawOption):
    if "page_info" in data and "media_info" in data["page_info"] and "retweeted_status" not in data:
        pic_url = data["page_info"]["page_pic"]
        pic_get = client.get(pic_url).content
        pic_bio = BytesIO(pic_get)
        pic = Image.open(pic_bio)
        pic_height =  math.floor(option.content_width / pic.width * pic.height)
        pic = pic.resize((option.content_width, pic_height))
        pic_time_box = Image.new("RGBA", (option.content_width, 50), (0, 0, 0, 150))
        pic.paste(pic_time_box, (0, pic_height - 50), pic_time_box)

        # 时长
        minutes, seconds = divmod(data["page_info"]["media_info"]["duration"], 60)
        hours, minutes = divmod(minutes, 60)
        video_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        time_font = ImageFont.truetype(font_bold, 30)
        draw = ImageDraw.Draw(pic)
        draw.text((10, pic_height - 50 + 5), video_time, "white", time_font)

        # 观看次数
        online_users = data["page_info"]["media_info"]["online_users"]
        online_users_size, _ = time_font.getsize(online_users)
        draw.text((option.content_width - online_users_size - 10, pic_height - 50 + 5), online_users, "white", time_font)
        return pic
    return None

async def draw_retweet(data, option: DrawOption):
    if "retweeted_status" in data:
        retweet_option = DefaultDrawOption()
        retweet_option.bg_width = option.content_width - 2 * option.margin
        retweet_option.bg_color = "#F5F5F5"
        retweet_data = data["retweeted_status"]
        if "page_info" in data:
            retweet_data["page_info"] = data["page_info"]

        retweet, retweet_url = await create_weibo_image(retweet_data, retweet_option)
        return retweet, retweet_url
    return None, []

def draw_info(data, option: DrawOption):
    icon_font = ImageFont.truetype(font_vanfont, 36)
    icon_color = (145, 145, 145)
    info_font = ImageFont.truetype(font_bold, 22)

    repost = str(data["reposts_count"])
    comment = str(data["comments_count"])
    attitudes = str(data["attitudes_count"])
    attitudes_size, _ = info_font.getsize(attitudes)

    info_bg = Image.new("RGB", (option.content_width, 60), option.bg_color)
    draw = ImageDraw.Draw(info_bg)
    draw.text((5 + 10, 10), "\uE012", icon_color, icon_font)
    draw.text((5 + 54, 17), repost, "#474747", info_font)
    draw.text((5 + 10 + option.content_width // 5 * 2, 10), "\uE639", icon_color, icon_font)
    draw.text((5 + 54 + option.content_width // 5 * 2, 17), comment, "#474747", info_font)
    draw.text((option.content_width - attitudes_size - 36 - 5, 10), "\uE63A", icon_color, icon_font)
    draw.text((option.content_width - attitudes_size, 17), attitudes, "#474747", info_font)

    return info_bg

def tcn_extract(text: str):
    if "t.cn" not in text:
        return None
    if not (weibo_id := re.compile(r"(http://t\.cn/\w{5,10})").findall(text)):
        return None
    return weibo_id
