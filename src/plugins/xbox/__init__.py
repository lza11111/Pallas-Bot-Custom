from pathlib import Path

from nonebot import on_message, get_driver
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.adapters.onebot.v11 import permission
from nonebot.permission import SUPERUSER
from httpx import HTTPStatusError

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse
from xbox.webapi.common.signed_session import SignedSession

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

        xbl_client = XboxLiveClient(auth_mgr)
        
        # Get profile
        profile_users = await xbl_client.people.get_friends_own_batch([auth_mgr.xsts_token.xuid])
        my_profile = profile_users.people[0]
        
        # Get friendslist
        friendslist = await xbl_client.people.get_friends_own()
        text = "看看谁在摸鱼:\n"
        count = 0
        for friend in friendslist.people:
            if friend.presence_state == "Online":
                text += f"{friend.modern_gamertag} is {friend.presence_text if friend.presence_text == 'Online' else f'playing {friend.presence_text}'} on {friend.presence_devices if friend.presence_devices is not None else 'PC'}\n"
                count += 1
        logger.info(f"Xbox Status: {my_profile}")
        if count == 0:
            text = "没人在摸鱼"
        await xbox_status_wrapper.finish(Message(f'[CQ:reply,id={event.message_id}]{str(text)}'))
