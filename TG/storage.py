from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Webs import *

import asyncio
import random
import string

from loguru import logger

import pyrogram.errors
from pyrogram.errors import PeerIdInvalid
from pyrogram.errors import FloodWait

import re

from bot import Vars, Bot

from typing import Any, Dict, List, Optional, Tuple



searchs = dict()
backs = dict()
chaptersList = dict()
queueList = dict()
pagination = dict()
subscribes = dict()

users_txt = """
<b>Welcome to the User Panel ! </b>

<b>=> Your ID: <code>{id}</code></b>
<b>=> File Name: <code>{file_name}</code><code>[{len}]</code></b>
<b>=> Caption: <code>{caption}</code></b>
<b>=> Thumbnail: <code>{thumb}</code></b>
<b>=> File Type: <code>{type}</code></b>
<b>=> PDF Password: <code>{password}</code></b>
<b>=> Megre Size: <code>{megre}</code></b>
<b>=> Regex/Zfill: <code>{regex}</code></b>
<b>=> Banner 1: <code>{banner1}</code></b>
<b>=> Banner 2: <code>{banner2}</code></b>
<b>=> Dump Channel: <code>{dump}</code></b>
<b>=> Compression Quality: <code>{compress}</code></b>
"""

web_data = {
    " Comick ": AllMangaScraper(),
    #" MangaMob ": MangaMobWebs(),
    " Asura Scans ": AsuraScansWebs(),
    #" Flame Comics": FlameComicsWebs(),
    #" Demonic Scans ": DemonicScansWebs(),
    " Manhua Fast ": ManhuaFastWebs(),
    " Weeb Central ": WeebCentralWebs(),
    " ManhwaClan ": ManhwaClanWebs(),
    " TempleToons ":TempleToonsWebs(),
    " Manhuaplus ": ManhuaplusWebs(),
    " Mgeko ": MgekoWebs(),
    " Manga18fx ": Manga18fxWebs(),
    " Manhwa18 ":  Manhwa18Webs(),
}

web_data = dict(sorted(web_data.items(), key=lambda x: x[0].strip()))

plugins_name = " ".join(web_data[i].sf for i in web_data.keys())


def split_list(li):
    return [li[x:x + 2] for x in range(0, len(li), 2)]


def check_get_web(url):
    for i in web_data.keys():
        if url.startswith(web_data[i].url):
            return web_data[i]


def plugins_list(type=None):
    button = []
    if type and type == "updates":
        for i in web_data.keys():
            c = web_data[i].sf
            c = f"udat_{c}"
            button.append(InlineKeyboardButton(i, callback_data=c))
    elif type and type == "gens":
        for i in web_data.keys():
            c = web_data[i].sf
            c = f"gens_{c}"
            button.append(InlineKeyboardButton(i, callback_data=c))
    elif type and type == "subs":
        for i in web_data.keys():
            c = web_data[i].sf
            c = f"isubs_{c}"
            button.append(InlineKeyboardButton(i, callback_data=c))
    else:
        for i in web_data.keys():
            c = web_data[i].sf
            c = f"plugin_{c}"
            button.append(InlineKeyboardButton(i, callback_data=c))

    button = split_list(button)
    button.append([InlineKeyboardButton("🔥 Close 🔥", callback_data="kclose")])
    return InlineKeyboardMarkup(button)


def get_webs(sf):
    for i in web_data.keys():
        if web_data[i].sf == sf:
            return web_data[i]


# retries an async awaitable as long as it raises FloodWait, and waits for err.x time
def retry_on_flood(function):

    async def wrapper(*args, **kwargs):
        while True:
            try:
                return await function(*args, **kwargs)

            except pyrogram.errors.FloodWait as err:
                logger.warning(
                    f'FloodWait, waiting {err.value} seconds: {err.MESSAGE}')
                await asyncio.sleep(err.value + 3)
                continue

            except ValueError:
                raise
            except pyrogram.errors.exceptions.bad_request_400.QueryIdInvalid:
                return
            except pyrogram.errors.exceptions.bad_request_400.MessageNotModified:
                return

            except Exception as err:
                logger.exception(err)
                raise err

    return wrapper



async def check_fsb(client, message):
    channel_button = []
    change_data = []

    for index, channel_information in enumerate(client.FSB):
        try:
            channel = int(channel_information[1])
        except:
            channel = str(channel_information[1])

        try:
            await client.get_chat_member(channel, message.from_user.id)
        except pyrogram.errors.UsernameNotOccupied:
            await retry_on_flood(
                client.send_message
            )(Vars.LOG_CHANNEL,
              f"`Channel does not exist, therefore bot will continue to operate normally ` : - {channel}"
              )

        except pyrogram.errors.ChatAdminRequired:
            await retry_on_flood(
                client.send_message
            )(Vars.LOG_CHANNEL,
              f"`Bot is not admin of the channel, therefore bot will continue to operate normally` :- `{channel}`"
              )

        except pyrogram.errors.UserNotParticipant:
            try:
                channel_link = channel_information[2]
            except:
                if isinstance(channel, int):
                    channel_link = await client.export_chat_invite_link(channel
                                                                        )
                else:
                    channel_link = f"https://telegram.me/{channel.strip()}"

            channel_button.append(
                InlineKeyboardButton(channel_information[0], url=channel_link))
            if len(channel_information) == 2:
                change_data.append((index, channel_information[0],
                                    channel_information[1], channel_link))

        except pyrogram.ContinuePropagation:
            raise
        except pyrogram.StopPropagation:
            raise
        except BaseException as e:
            await retry_on_flood(
                client.send_message
            )(Vars.LOG_CHANNEL,
              f"<i>Error at Force Subscribe : - `{e}` at Channel : - {channel}</i>"
              )
    
    return channel_button, change_data



class AQueue:
    def __init__(self, maxsize: Optional[int] = None):
        """
        storage_data: {task_id: {data: data, priority: priority, user_id: user_id}}
        data_users: {user_id: [task_id1, task_id2, task_id3]}
        ongoing_tasks: {task_id: task_data} - tasks currently being processed
        """
        self.storage_data: Dict[str, Dict] = {}
        self.data_users: Dict[int, List[str]] = {}
        self.ongoing_tasks: Dict[str, Dict] = {}
        self.lock = asyncio.Lock()
        self.maxsize = maxsize

    async def get_random_id(self) -> str:
        """Generate a unique random task ID."""
        while True:
            random_string = ''.join(
                random.choices(string.ascii_letters + string.digits + string.ascii_lowercase + string.ascii_uppercase, k=5))  
            
            if random_string not in self.storage_data and random_string not in self.ongoing_tasks:
                return random_string

    
    async def put(self, data: Any, user_id: int, priority: int = 1) -> str:
        """
        Add a new task to the queue.

        Args:
            user_id: User identifier
            data: Task data
            priority: 0 for premium users, 1 for normal users

        Returns:
            task_id: Generated task ID
        """
        if self.maxsize is not None and len(self.storage_data) >= self.maxsize:
            raise asyncio.QueueFull("Queue has reached maximum size")

        async with self.lock:
            task_id = await self.get_random_id()
            self.storage_data[task_id] = {
                'data': data, 
                'priority': priority, 
                'user_id': user_id,
            }

            if user_id not in self.data_users:
                self.data_users[user_id] = []

            self.data_users[user_id].append(task_id)

            return task_id

    
    async def get(self, worker_id: int) -> Tuple[Any, int, str]:
        """
        Get the next available task from the queue.

        Args:
            worker_id: ID of the worker requesting the task

        Returns:
            Tuple of (task_data, user_id, task_id)
        """
        while True:
            async with self.lock:
                if not self.storage_data:
                    await asyncio.sleep(0.1)
                    continue

                available_tasks = []
                for task_id, data in self.storage_data.items():
                    user_id = data['user_id']
                    user_has_ongoing = any(
                        task_data['user_id'] == user_id 
                        for task_data in self.ongoing_tasks.values()
                    )

                    if not user_has_ongoing:
                        available_tasks.append((task_id, data))

                if not available_tasks:
                    await asyncio.sleep(0.1)
                    continue

                premium_tasks = [task for task in available_tasks if task[1]['priority'] == 0]

                if premium_tasks:
                    selected_task = premium_tasks[0]
                else:
                    selected_task = available_tasks[0]

                task_id, task_data = selected_task

                self.ongoing_tasks[task_id] = task_data
                del self.storage_data[task_id]

                user_id = task_data['user_id']
                if user_id in self.data_users and task_id in self.data_users[user_id]:
                    self.data_users[user_id].remove(task_id)
                    
                    if not self.data_users[user_id]:
                        del self.data_users[user_id]

                return task_data['data'], user_id, task_id

    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a specific task by its ID.

        Returns:
            bool: True if task was found and deleted, False otherwise
        """
        async with self.lock:
            if task_id in self.storage_data:
                task_data = self.storage_data[task_id]
                user_id = task_data['user_id']

                # Remove from storage
                del self.storage_data[task_id]

                # Remove from user's task list
                if user_id in self.data_users and task_id in self.data_users[user_id]:
                    self.data_users[user_id].remove(task_id)
                    if not self.data_users[user_id]:
                        del self.data_users[user_id]

                return True
            return False

    
    async def delete_tasks(self, user_id: int) -> int:
        """Delete all tasks for a specific user.

        Returns:
            int: Number of tasks successfully deleted
        """
        if user_id not in self.data_users:
                return 0

        task_ids = self.data_users.pop(user_id)
        deleted_count = 0

        for task_id in task_ids:
            if task_id in self.storage_data:
                sts = self.storage_data[task_id]['data'][3]
                if sts:
                    try: 
                        await sts.delete()
                    except FloodWait as e: 
                        await asyncio.sleep(e.value+2)
                        await sts.delete()
                    except:
                        pass
                
                del self.storage_data[task_id]
                deleted_count += 1

        if user_id in self.data_users:
            del self.data_users[user_id]

        return deleted_count

    
    def get_count(self, user_id: int) -> int:
        """Get the number of pending tasks for a user."""
        return len(self.data_users[user_id]) if user_id in self.data_users else 0

    
    def task_exists(self, task_id: str) -> bool:
        """Check if a task exists in the queue (pending or ongoing)."""
        return task_id in self.storage_data or task_id in self.ongoing_tasks

    
    def qsize(self) -> int:
        """Return the number of pending items in the queue."""
        return len(self.storage_data)

    
    def empty(self) -> bool:
        """Return True if the queue is empty."""
        return not self.storage_data

    
    async def task_done(self, task_id: str) -> bool:
        """Mark a task as done and remove it from ongoing tasks.

        Returns:
            bool: True if task was found and marked as done, False otherwise
        """
        async with self.lock:
            if task_id in self.ongoing_tasks:
                user_id = self.ongoing_tasks[task_id]['user_id']
                if user_id in self.data_users and task_id in self.data_users[user_id]:
                    self.data_users[user_id].remove(task_id)
                
                del self.ongoing_tasks[task_id]
                return True
            return False
        
    def get_ongoing_count(self, user_id: int) -> int:
        """Get the number of ongoing tasks for a user."""
        return sum(1 for task in self.ongoing_tasks.values() if task['user_id'] == user_id)


queue = AQueue()
    


def clean(txt, length=-1):
    txt = txt.replace("_", "").replace("&", "").replace(";", "")
    txt = txt.replace("None", "").replace(":", "").replace("'", "")
    txt = txt.replace("|", "").replace("*", "").replace("?", "")
    txt = txt.replace(">", "").replace("<", "").replace("`", "")
    txt = txt.replace("!", "").replace("@", "").replace("#", "")
    txt = txt.replace("$", "").replace("%", "").replace("^", "")
    txt = txt.replace("~", "").replace("+", "").replace("=", "")
    txt = txt.replace("/", "").replace("\\", "").replace("\n", "")
    if length != -1:
        txt = txt[:length]
    return txt


def get_episode_number(text):
    text = str(text)
    pattern1 = re.compile(r"Chapter\s+(\d+(?:\.\d+)?)")
    pattern2 = re.compile(r"Volume\s+(\d+) Chapter\s+(\d+(?:\.\d+)?)")
    pattern3 = re.compile(r"Chapter\s+(\d+)\s+-\s+(\d+(?:\.\d+)?)")
    patternX = re.compile(r"(\d+(?:\.\d+)?)")

    match1 = re.search(pattern1, text)
    if match1:
        return str(match1.group(1))

    match2 = re.search(pattern2, text)
    if match2:
        return str(match2.group(2))

    match3 = re.search(pattern3, text)
    if match3:
        return str(match3.group(1))

    matchX = re.search(patternX, text)
    if matchX:
        return str(matchX.group(1))
