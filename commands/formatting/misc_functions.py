async def get_avatar_url(ctx, user):
    from main import bot
    with ctx:
        user = bot.get_user(user)
        user_avatar = user.avatar_url.BASE + user.avatar_url._url
        return user_avatar
    
# adds commas to a number to make it easier to read
def format_number(number):
    number = "{:,}".format(number)
    return number