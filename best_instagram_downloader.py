from functions import *

bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, start_msg, parse_mode="Markdown", disable_web_page_preview=True)
    log(f"{bot_username} log:\n\nuser: {message.chat.id}\n\nstart command")

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, help_msg, parse_mode="Markdown", disable_web_page_preview=True)
    log(f"{bot_username} log:\n\nuser: {message.chat.id}\n\nhelp command")

@bot.message_handler(regexp = insta_post_reg)
def handle_correct_spotify_link(message):
    guide_msg_1 = bot.send_message(message.chat.id, "Ok wait a few moments...")

    post_shortcode = get_post_shortcode_from_link(message.text)
    print("shortcode:", post_shortcode)

    if not post_shortcode:
        log(f"{bot_username} log:\n\nuser: {message.chat.id}\n\nerror in getting post_shortcode")
        return # post shortcode not found

    L = get_ready_to_work_insta_instance()
    post = Post.from_shortcode(L.context, post_shortcode)

    # caption handling
    new_caption = post.caption
    while len(new_caption) + len(caption_trail) > 1024:
        new_caption = new_caption[:-1] # remove last character
    new_caption = new_caption + caption_trail

    # handle post with single media
    try_to_delete_message(message.chat.id, guide_msg_1.message_id)
    if post.mediacount == 1:
        if post.is_video:
            print("single video")
            bot.send_video(message.chat.id, post.video_url, caption=new_caption)
        else:
            print("single image")
            bot.send_photo(message.chat.id, post.url, caption=new_caption)
        bot.send_message(message.chat.id, end_msg, parse_mode="Markdown", disable_web_page_preview=True)
        return

    # handle post with multiple media
    media_list = []
    sidecars = post.get_sidecar_nodes()
    for s in sidecars:
        if s.is_video: # it's a video
            url = s.video_url
            media = telebot.types.InputMediaVideo(url)
            if not media_list: # first media of post
                media = telebot.types.InputMediaVideo(url, caption=new_caption)
        else: # it's an image
            url = s.display_url
            media = telebot.types.InputMediaPhoto(url)
            if not media_list: # first media of post
                media = telebot.types.InputMediaPhoto(url, caption=new_caption)
        media_list.append(media)
    print("media group")
    try_to_delete_message(message.chat.id, guide_msg_1.message_id)
    bot.send_media_group(message.chat.id, media_list)
    bot.send_message(message.chat.id, end_msg, parse_mode="Markdown", disable_web_page_preview=True)
    return

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_message(message.chat.id, wrong_pattern_msg, parse_mode="Markdown", disable_web_page_preview=True)

bot.infinity_polling()

