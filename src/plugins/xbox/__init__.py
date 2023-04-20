from pathlib import Path

from nonebot import on_message, get_driver
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.adapters.onebot.v11 import permission
from nonebot.permission import SUPERUSER
from nonebot.exception import ActionFailed
from httpx import HTTPStatusError

from xbox.webapi.api.client import XboxLiveClient, DefaultXboxLiveLanguages
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse
from xbox.webapi.common.signed_session import SignedSession

from .utils import query_member_qq_id
from src.common.utils import to_image

global_config = get_driver().config

tokens_file = Path(__file__).parent.parent.parent.parent.joinpath("tokens.json")

xbox_status_wrapper = on_message(
    priority=14,
    block=False,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER,
)

@xbox_status_wrapper.handle()
async def xbox_status_wrapper_main(bot: Bot, event: GroupMessageEvent, state: T_State):
    message_str = str(event.get_message())
    if "谁在摸鱼" not in message_str:
        return
    async with SignedSession() as session:
        auth_mgr = AuthenticationManager(session, global_config.aad_client_id, global_config.aad_client_secret, "")
        try:
            with open(tokens_file) as f:
                tokens = f.read()
            auth_mgr.oauth = OAuth2TokenResponse.parse_raw(tokens)
        except FileNotFoundError as e:
            logger.error(
                f"File {tokens_file} isn`t found or it doesn`t contain tokens! err={e}"
            )
            return
        try:
            await auth_mgr.refresh_tokens()
        except HTTPStatusError as e:
            logger.error(
                f"""
                Could not refresh tokens from {tokens_file}, err={e}\n
                You might have to delete the tokens file and re-authenticate 
                if refresh token is expired
            """
            )
            return

        # Save the refreshed/updated tokens
        with open(tokens_file, mode="w") as f:
            f.write(auth_mgr.oauth.json())

        xbl_client = XboxLiveClient(auth_mgr, language=DefaultXboxLiveLanguages.Hong_Kong)
        
        # Get group member list
        member_list = await bot.get_group_member_list(group_id=event.group_id)

        # Get profile
        profile_users = await xbl_client.people.get_friends_own_batch([auth_mgr.xsts_token.xuid])
        my_profile = profile_users.people[0]
        
        # Get friendslist
        friendslist = await xbl_client.people.get_friends_own()
        friendslist.people.append(my_profile)
        text = "看看谁在摸鱼:\n"
        count = 0
        friendslist.people.sort(key=lambda x: x.presence_state, reverse=True)
        for friend in friendslist.people:
            logger.info(friend)
            for member in member_list:
                if member["user_id"] == query_member_qq_id(event.group_id, friend.xuid):
                    nickname = member['card'] if member['card'] else member['nickname']
                    if friend.presence_details is None or len(friend.presence_details) == 0:
                        presence_text = 'Offline'
                        presence_icon = '🔴'
                        text += f"[{presence_icon}] {nickname} is {presence_text}\n"
                    else:
                        if any([details.state == 'Active' for details in friend.presence_details]):
                            presence_text = " and ".join([f'{details.presence_text} on {details.device}' for details in friend.presence_details]) if friend.presence_details is not None else "None"
                            presence_icon = "🎮" if any([details.is_game for details in friend.presence_details]) else "🟢"
                            text += f"{presence_icon} {nickname} is {friend.presence_text if friend.presence_text == 'Online' else f'playing {presence_text}'}\n"
                        else:
                            presence_text = friend.presence_text
                            presence_icon = '🔴'
                            text += f"{presence_icon} {nickname} {friend.presence_text}\n"
                    count += 1
        if count == 0:
            text = "没人在摸鱼"
        try:
            await xbox_status_wrapper.finish(text)
        except ActionFailed:
            await xbox_status_wrapper.finish(MessageSegment.image(file=to_image(text)))
