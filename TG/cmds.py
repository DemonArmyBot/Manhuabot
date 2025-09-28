from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .storage import *
import pyrogram.errors

from bot import Bot, Vars, logger

import random
from Tools.db import *
from Tools.my_token import check_token_, verify_token

from pyrogram.handlers import MessageHandler
import time

from asyncio import create_subprocess_exec
from os import execl
from sys import executable

import shutil, psutil, time, os, platform
import asyncio

import pytz
from datetime import datetime

HELP_MSG = """
<b>To download a manga just type the name of the manga you want to keep up to date.</b>

For example:
`Overflow🙂`

<blockquote expandable><i>Then you will have to choose the language of the manga. Depending on this language, you will be able to choose the website where you could download the manga. Here you will have the option to subscribe, or to choose a chapter to download. The chapters are sorted according to the website.</i></blockquote>

<blockquote><b>Updates Channel : @DemonArmy</b></blockquote>
"""

@Bot.on_message(filters.private)
async def on_private_message(client, message):
  channel = Vars.FORCE_SUB_CHANNEL
  if channel in ["None", None, "none", "OFF", False, "False", ""]:
    return message.continue_propagation()

  if not client.FSB or client.FSB == []:
    return message.continue_propagation()

  channel_button, change_data = await check_fsb(client, message)
  if not channel_button:
    return message.continue_propagation()

  channel_button = split_list(channel_button)
  channel_button.append(
    [InlineKeyboardButton("🔃 Refresh 🔃", callback_data="refresh")]
  )

  await retry_on_flood(message.reply_photo)(
    caption=Vars.FORCE_SUB_TEXT,
    photo=random.choice(Vars.PICS),
    reply_markup=InlineKeyboardMarkup(channel_button),
    quote=True,
  )
  if change_data:
    for change_ in change_data:
      client.FSB[change_[0]] = (change_[1], change_[2], change_[3])


@Bot.on_message(filters.command("info") & filters.user(Vars.ADMINS))
async def get_info_(client, message):
  sts = await message.reply("<code>Processing...</code>")
  try:
    user_id = str(message.text.split(" ")[1])
    if user_id in uts:
      txt = f"<b>User ID: {user_id}</b>\n"
      txt += f"<b>File Name: {uts[user_id]['setting'].get('file_name', 'None')}</b>\n"
      txt += f"<b>Caption: {uts[user_id]['setting'].get('caption', 'None')}</b>\n"
      txt += f"<b>Thumb: {uts[user_id]['setting'].get('thumb', 'None')}</b>\n"
      txt += f"<b>Banner1: {uts[user_id]['setting'].get('banner1', 'None')}</b>\n"
      txt += f"<b>Banner2: {uts[user_id]['setting'].get('banner2', 'None')}</b>\n"
      txt += f"<b>Dump: {uts[user_id]['setting'].get('dump', 'None')}</b>\n"
      txt += f"<b>Type: {uts[user_id]['setting'].get('type', 'None')}</b>\n"
      txt += f"<b>Megre: {uts[user_id]['setting'].get('megre', 'None')}</b>\n"
      txt += f"<b>Regex: {uts[user_id]['setting'].get('regex', 'None')}</b>\n"
      txt += f"<b>File Name Len: {uts[user_id]['setting'].get('file_name_len', 'None')}</b>\n"
      txt += f"<b>Password: {uts[user_id]['setting'].get('password', 'None')}</b>\n"
      txt += f"<b>Compress: {uts[user_id]['setting'].get('compress', 'None')}</b>\n"
      await retry_on_flood(sts.edit)(txt)
    else:
      uts[str(user_id)] = {}
      uts[str(user_id)]['setting'] = {}
      sync()
      await retry_on_flood(sts.edit)("<code>User Not Found</code>")
  except Exception as err:
    await retry_on_flood(sts.edit)(err)



@Bot.on_message(filters.command("my_plan"))
async def my_plan(client, message):
  plan = await premium_user(message.from_user.id)
  if plan:
    xt = (plan["expiration_timestamp"] - (time.time()))
    x = round(xt / (24 * 60 * 60))
    await message.reply(f"""
<i>Your Information:</i>

  <b>- User ID: {message.from_user.id}</b>
  <b>- Username: {message.from_user.username}</b>
  <b>- Days: {plan["Days"]}</b>
  <b>- Expiration Days: {x}</b> 
  
<i>Thanks For Buying It......</i>""",
                        quote=True,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                            " Close ", callback_data="kclose")]])
                       )
  else:
    await message.reply(
      "<i> You Have No Plan!! </i>",
      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" Buy Now ", callback_data="premuim")]])
                       )


@Bot.on_message(
  filters.command(["clean_tasks", "clean_queue"]))
async def deltask(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")
    
  if queue.get_count(message.from_user.id):
    numb = await queue.delete_tasks(message.from_user.id)
    await message.reply(f"<i>All Your Tasks Deleted:- {numb} </i>")
  else:
    await message.reply("<i>There is no any your pending tasks.... </i>")
  

@Bot.on_message(filters.command("start"))
async def start(client, message):

  if str(message.from_user.id) not in uts:
    uts[str(message.from_user.id)] = {}
    sync()

  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")

  if len(message.command) > 1:
    if message.command[1] != "start":
      user_id = message.from_user.id
      token = message.command[1]
      sts = await message.reply("<i>ㅤProcessing.....</i>")
      return await verify_token(sts, user_id, token)
  
  photo = random.choice(Vars.PICS)
  ping = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - Vars.PING))
  await message.reply_photo(
      photo,
      caption=
      ("<b><i>Welcome to the best manga pdf bot in telegram!!</i></b>\n"
       "\n"
       "<b><i>How to use? Just type the name of some manga you want to keep up to date.</i></b>\n"
       "\n"
       "<b><i>For example:</i></b>\n"
       "<i><code>One Piece</i></code>\n"
       "\n"
       f"<b><i>Ping:- {ping}</i></b>"
       "\n"
       "<b><i>Check /help for more information.</i></b>"),
      reply_markup=InlineKeyboardMarkup([
        [
          InlineKeyboardButton('✯ Repo ✯', url="https://github.com/DemonArmyBot/Manhwabot"),
          InlineKeyboardButton("✯ Support ✯", url="https://t.me/DemonArmy")
        ],
        [
          InlineKeyboardButton("♛ Setting ♛", callback_data="mus"),
          InlineKeyboardButton("♞ Close ♞", callback_data="kclose")
        ]
      ]))

  

@Bot.on_message(
    filters.command(["add", "add_premium"]) & filters.user(Bot.ADMINS))
async def add_handler(_, msg):
  sts = await msg.reply_text("<code>Processing...</code>")
  try:
    user_id = int(msg.text.split(" ")[1])
    time_limit_days = int(msg.text.split(" ")[2])
    await add_premium(user_id, time_limit_days)
    await retry_on_flood(sts.edit
                         )("<code>User added to premium successfully.</code>")
    try:
      await retry_on_flood(_.send_message
                         )(user_id, f"<i>You are now a premium user for {time_limit_days} days... Thanks For Buying It.....</i>")
    except:
      pass
  except Exception as err:
    await retry_on_flood(sts.edit)(err)


@Bot.on_message(
    filters.command(["del", "del_premium"]) & filters.user(Bot.ADMINS))
async def del_handler(_, msg):
  sts = await msg.reply_text("<code>Processing...</code>")
  try:
    user_id = int(msg.text.split(" ")[1])
    await remove_premium(user_id)
    await retry_on_flood(
        sts.edit)("<code>User removed from premium successfully.</code>")
    try:
      await retry_on_flood(_.send_message
                         )(user_id, "<i>Your Premuims Plans End.. Please Buy again or Contact To Owner....  .</i>")
    except:
      pass
  except Exception as err:
    await retry_on_flood(sts.edit)(err)


@Bot.on_message(
    filters.command(["del_expired", "del_expired_premium"])
    & filters.user(Bot.ADMINS))
async def del_expired_handler(_, msg):
  sts = await msg.reply_text("<code>Processing...</code>")
  try:
    await remove_expired_users()
    await retry_on_flood(sts.edit
                         )("<code>Expired users removed successfully.</code>")
  except Exception as err:
    await retry_on_flood(sts.edit)(err)


@Bot.on_message(
    filters.command(["premium", "premium_users"]) & filters.user(Bot.ADMINS))
async def premium_handler(_, msg):
  sts = await msg.reply_text("<code>Processing...</code>")
  try:
    txt = "<b>Premium Users:-</b>\n"
    async for user_ids, data in get_all_premuim():
      user_info = await _.get_users(user_ids)
      username = user_info.username
      first_name = user_info.first_name
      expiration_timestamp = data["expiration_timestamp"]
      xt = (expiration_timestamp - (time.time()))
      x = round(xt / (24 * 60 * 60))
      txt += f"User id: <code>{user_ids}</code>\nUsername: @{username}\nName: <code>{first_name}</code>\nExpiration Timestamp: {x} days\n"

    await retry_on_flood(sts.edit)(txt[:1024])
  except Exception as err:
    await retry_on_flood(sts.edit)(err)


@Bot.on_message(filters.command(["broadcast", "b"]) & filters.user(Bot.ADMINS))
async def b_handler(_, msg):
  return await borad_cast_(_, msg)


@Bot.on_message(
    filters.command(["pbroadcast", "pb"]) & filters.user(Bot.ADMINS))
async def pb_handler(_, msg):
  return await borad_cast_(_, msg, True)


async def borad_cast_(_, message, pin=None):

  def del_users(user_id):
    try:
      user_id = str(user_id)
      del uts[user_id]
      sync(_.DB_NAME, 'uts')
    except:
      pass

  sts = await message.reply_text("<code>Processing...</code>")
  if message.reply_to_message:
    user_ids = get_users()
    msg = message.reply_to_message
    total = 0
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0
    await retry_on_flood(sts.edit)("<code>Broadcasting...</code>")
    for user_id in user_ids:
      try:
        docs = await msg.copy(int(user_id))
        if pin:
          await docs.pin(both_sides=True)

        successful += 1
      except FloodWait as e:
        await asyncio.sleep(e.value)

        docs = await msg.copy(int(user_id))
        if pin:
          await docs.pin(both_sides=True)

        successful += 1
      except pyrogram.errors.UserIsBlocked:
        del_users(user_id)
        blocked += 1
      except pyrogram.errors.PeerIdInvalid:
        del_users(user_id)
        unsuccessful += 1
      except pyrogram.errors.InputUserDeactivated:
        del_users(user_id)
        deleted += 1
      except pyrogram.errors.UserNotParticipant:
        del_users(user_id)
        blocked += 1
      except:
        unsuccessful += 1

    status = f"""<b><u>Broadcast Completed</u>

    Total Users: <code>{total}</code>
    Successful: <code>{successful}</code>
    Blocked Users: <code>{blocked}</code>
    Deleted Accounts: <code>{deleted}</code>
    Unsuccessful: <code>{unsuccessful}</code></b>"""

    await retry_on_flood(sts.edit)(status)
  else:
    await retry_on_flood(sts.edit
                         )("<code>Reply to a message to broadcast it.</code>")



@Bot.on_message(filters.command("restart") & filters.user(Bot.ADMINS))
async def restart_(client, message):
  msg = await message.reply_text("<code>Restarting.....</code>", quote=True)
  with open("restart_msg.txt", "w") as file:
    file.write(str(msg.chat.id) + ":" + str(msg.id))
    file.close()

  await (await create_subprocess_exec("python3", "update.py")).wait()
  execl(executable, executable, "-B", "main.py")


def get_nepal_time():
  try:
      # Set timezone to Asia/Kathmandu
      kathmandu_tz = pytz.timezone('Asia/Kathmandu')
      nepaltime = datetime.now(kathmandu_tz)
      return nepaltime.strftime("%Y-%m-%d %I:%M:%S %p %Z")
  except:
      return "N/A"

def humanbytes(size):
    if not size:
        return ""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units) - 1:
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


@Bot.on_message(filters.command('stats'))
async def show_stats(client, message):
    total_disk, used_disk, free_disk = shutil.disk_usage(".")
    total_disk_h = humanbytes(total_disk)
    used_disk_h = humanbytes(used_disk)
    free_disk_h = humanbytes(free_disk)
    disk_usage_percent = psutil.disk_usage('/').percent

    net_start = psutil.net_io_counters()
    time.sleep(2)
    net_end = psutil.net_io_counters()

    bytes_sent = net_end.bytes_sent - net_start.bytes_sent
    bytes_recv = net_end.bytes_recv - net_start.bytes_recv

    cpu_cores = os.cpu_count()
    cpu_usage = psutil.cpu_percent()

    ram = psutil.virtual_memory()
    ram_total = humanbytes(ram.total)
    ram_used = humanbytes(ram.used)
    ram_free = humanbytes(ram.available)
    ram_usage_percent = ram.percent

    try:
        uptime_seconds = time.time() - Vars.PING
        uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime_seconds))
    except:
        uptime = "N/A"

    start_time = time.time()
    status_msg = await message.reply('📊 **Accessing System Details...**')
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000

    os_name = platform.system()
    os_version = platform.release()
    python_version = platform.python_version()

    response_text = f"""
🖥️ **System Statistics Dashboard**

💾 **Disk Storage**
├ Total:  `{total_disk_h}`
├ Used:  `{used_disk_h}` ({disk_usage_percent}%)
└ Free:  `{free_disk_h}`

🧠 **RAM (Memory)**
├ Total:  `{ram_total}`
├ Used:  `{ram_used}` ({ram_usage_percent}%)
└ Free:  `{ram_free}`

⚡ **CPU**
├ Cores:  `{cpu_cores}`
└ Usage:  `{cpu_usage}%`

🌐 **Network**
├ Upload Speed:  `{humanbytes(bytes_sent/2)}/s`
├ Download Speed:  `{humanbytes(bytes_recv/2)}/s`
└ Total I/O:  `{humanbytes(net_end.bytes_sent + net_end.bytes_recv)}`

📟 **System Info**
├ OS:  `{os_name}`
├ OS Version:  `{os_version}`
├ Python:  `{python_version}`
├ Time:  `{get_nepal_time()}`
└ Uptime:  `{uptime}`

⏱️ **Performance**
└ Current Ping:  `{time_taken_ms:.3f} ms`
"""

    await message.reply_text(response_text, quote=True)
    await status_msg.delete()


@Bot.on_message(filters.command("shell") & filters.user(Bot.ADMINS))
async def shell(_, message):
  cmd = message.text.split(maxsplit=1)
  if len(cmd) == 1:
    return await message.reply("<code>No command to execute was given.</code>")

  cmd = cmd[1]
  proc = await asyncio.create_subprocess_shell(cmd,
                                               stdout=asyncio.subprocess.PIPE,
                                               stderr=asyncio.subprocess.PIPE)
  stdout, stderr = await proc.communicate()
  stdout = stdout.decode().strip()
  stderr = stderr.decode().strip()
  reply = ""
  if len(stdout) != 0:
    reply += f"<b>Stdout</b>\n<blockquote>{stdout}</blockquote>\n"
  if len(stderr) != 0:
    reply += f"<b>Stderr</b>\n<blockquote>{stderr}</blockquote>"

  if len(reply) > 3000:
    file_name = "shell_output.txt"
    with open(file_name) as out_file:
      await message.reply_document(out_file)
      out_file.close()
    os.remove(file_name)
  elif len(reply) != 0:
    await message.reply(reply)
  else:
    await message.reply("No Reply")


@Bot.on_message(filters.command("export") & filters.user(Bot.ADMINS))
async def export_(_, message):
  cmd = message.text.split(maxsplit=1)
  if len(cmd) == 1:
    return await message.reply("<code>File Name Not given.</code>")

  sts = await message.reply("<code>Processing...</code>")
  try:
    file_name = cmd[1]
    if "*2" in file_name:
      file_name = file_name.replace("*2", "")
      file_name = f"__{file_name}__"

    if os.path.exists(file_name):
      await message.reply_document(file_name)
    else:
      await sts.edit("<code>File Not Found</code>")
  except Exception as err:
    await sts.edit(err)


@Bot.on_message(filters.command("import") & filters.user(Bot.ADMINS))
async def import_(_, message):
  cmd = message.text.split(maxsplit=1)
  if len(cmd) == 1:
    return await message.reply("<code>File Name Not given.</code>")

  sts = await message.reply("<code>Processing...</code>")
  try:
    file_name = cmd[1]
    if "*2" in file_name:
      file_name = file_name.replace("*2", "")
      file_name = f"__{file_name}__"

    if not os.path.exists(file_name):
      await message.download(file_name, file_name=file_name)
    else:
      await sts.edit("<code>File Path Found</code>")
  except Exception as err:
    await sts.edit(err)


@Bot.on_message(filters.command(["clean", "c"]) & filters.user(Bot.ADMINS))
async def clean(_, message):
  directory = '/app'
  ex = (".mkv", ".mp4", ".zip", ".pdf", ".png", ".epub", ".temp")
  protected_dirs = (".git", "venv", "env", "__pycache__"
                    )  # Directories to SKIP
  sts = await message.reply_text("🔍 Cleaning files...")
  deleted_files = []
  removed_dirs = []

  if os.path.exists("Process"):
    shutil.rmtree("Process")
  elif os.path.exists("./Process"):
    shutil.rmtree("./Process")

  try:
    for root, dirs, files in os.walk(directory, topdown=False):
      # Skip protected directories (e.g., .git)
      dirs[:] = [d for d in dirs if d not in protected_dirs]
      for file in files:
        if file.lower().endswith(ex):
          file_path = os.path.join(root, file)
          try:
            os.remove(file_path)
            deleted_files.append(file_path)
          except Exception as e:
            pass

        elif file.lower().startswith("vol"):
          file_path = os.path.join(root, file)
          try:
            os.remove(file_path)
            deleted_files.append(file_path)
          except Exception as e:
            pass

      for dir_name in dirs:
        dir_path = os.path.join(root, dir_name)
        try:
          if not os.listdir(dir_path):  # Check if empty
            os.rmdir(dir_path)
            removed_dirs.append(dir_path)

          elif dir_path == "/app/Downloads":
            os.rmdir("/app/Downloads")
            removed_dirs.append("/app/Downloads")

          elif dir_path == "/app/downloads":
            os.rmdir("/app/downloads")
            removed_dirs.append("/app/downloads")

          try:
            dir_path = int(dir_path)
            os.rmdir(dir_path)
            removed_dirs.append(dir_path)
          except:
            pass
        except Exception as e:
          pass

    msg = "**🧹 Cleaning Logs:**\n"
    if deleted_files:
      msg += f"🗑 **Deleted {len(deleted_files)} files:**\n" + "\n".join(
          deleted_files[:10])  # Show first 10
      if len(deleted_files) > 10:
        msg += f"\n...and {len(deleted_files) - 10} more."
      else:
        msg += "✅ No files deleted."

    if removed_dirs:
      msg += f"\n\n📁 **Removed {len(removed_dirs)} empty directories:**\n" + "\n".join(
          removed_dirs[:5])
      if len(removed_dirs) > 5:
        msg += f"\n...and {len(removed_dirs) - 5} more."

    await sts.edit(msg[:4096])  # Telegram's max message length
  except Exception as err:
    await sts.edit(f"❌ Error: {str(err)}")


def remove_dir(path):
  try:
    if os.path.exists(path):
      for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
          os.remove(os.path.join(root, file))
          for dir in dirs:
            os.rmdir(os.path.join(root, dir))
      os.rmdir(path)
  except Exception as err:
    return err


@Bot.on_message(filters.command("queue"))
async def queue_msg_handler(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")
  
  _datas_ = list(queue.ongoing_tasks.values())
  reply_txt = f"<blockquote><b>📌 Queue Status (Total: {str(queue.qsize())} chapters)</b></blockquote>\n\n"
  reply_txt += f"<b>👤 Your queue:</b>"
  
  _processing = []
  _user_count = queue.get_count(message.from_user.id)
  if _user_count and int(_user_count) != 0:
    reply_txt+= f"""<blockquote expandable>=> <i>Total Chapters: {_user_count}</i>\n"""
    if _datas_:
      value = next((data['data'] for data in _datas_ if data['user_id'] == message.from_user.id), None)
      value = value[0] if value else None
      if value:
        reply_txt += f"=> <i>{value['manga_title']} - {value['title']}</i></blockquote>\n"
      else:
        reply_txt += "</blockquote>\n"
  else:
    reply_txt += "\n=> <i>No chapters in your queue.</i>\n"
  
  reply_txt += "\n**🚦 Now Processing:**\n"
  if _datas_:
    reply_txt += "<blockquote expandable>"
    for i, data in enumerate(_datas_, 1):
      user_query = data['data'][2]
      reply_txt += f"{i}. {user_query.from_user.mention()}\n"
      _processing.append(user_query.from_user.id)
      if i == 3:
        break
    reply_txt += "</blockquote>\n"
  else:
    reply_txt += "=> <i>No chapters in global queue.</i>\n"

  sample_txt = ""
  sample_txt += "\n**⏳ Waiting Line:**\n"
  if queue.qsize() > 0:
    reply_txt += "<blockquote expandable>"
    for i, data in enumerate(queue.storage_data.values(), 1):
      user_query = data['data'][2]
      if user_query.from_user.id not in _processing:
        sample_txt += f"{i}. {user_query.from_user.mention()}\n"
        if i == 2:
          break
    sample_txt += "=> <i>Other chapters are in the waiting line.</i>"
    sample_txt += "</blockquote>\n"
  else:
    sample_txt += "=> <i>No chapters in waiting line.</i>\n"

  if int(len(reply_txt) + len(sample_txt)) < 4096:
    reply_txt += sample_txt
  
  await retry_on_flood(message.reply_text)(
    reply_txt,
    quote=True,
    reply_markup=InlineKeyboardMarkup([
      [
        InlineKeyboardButton("🗑 Clean Queue 🗑", callback_data="clean_queue"),
        InlineKeyboardButton("🪦 Subscription 🪦", callback_data="isubs")
      ],
      [
        InlineKeyboardButton("⚔️ Close ⚔️", callback_data="kclose"),
        InlineKeyboardButton("🔄 Refresh 🔄", callback_data="refresh_queue")
      ],
      [
        InlineKeyboardButton(" ♕ Owner ♕", user_id=Vars.OWNER)
      ]
    ])
  )


@Bot.on_message(filters.command(["us", "user_setting", "user_panel"]))
async def userxsettings(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")

  sts = await message.reply("<code>Processing...</code>")
  try:
    user_id = str(message.from_user.id)
    if not user_id in uts:
      uts[user_id] = {}
      sync()

    if not "setting" in uts[user_id]:
      uts[user_id]['setting'] = {}
      sync()

    thumbnali = uts[user_id]['setting'].get("thumb", None)
    if thumbnali:
      thumb = "True" if not thumbnali.startswith("http") else thumbnali
    else:
      thumb = thumbnali

    banner1 = uts[user_id]['setting'].get("banner1", None)
    banner2 = uts[user_id]['setting'].get("banner2", None)
    if banner1:
      banner1 = "True" if not banner1.startswith("http") else banner1

    if banner2:
      banner2 = "True" if not banner2.startswith("http") else banner2

    txt = users_txt.format(
        id=user_id,
        file_name=uts[user_id]['setting'].get("file_name", "None"),
        caption=uts[user_id]['setting'].get("caption", "None"),
        thumb=thumb,
        banner1=banner1,
        banner2=banner2,
        dump=uts[user_id]['setting'].get("dump", "None"),
        type=uts[user_id]['setting'].get("type", "None"),
        megre=uts[user_id]['setting'].get("megre", "None"),
        regex=uts[user_id]['setting'].get("regex", "None"),
        len=uts[user_id]['setting'].get("file_name_len", "None"),
        password=uts[user_id]['setting'].get("password", "None"),
        compress=uts[user_id]['setting'].get("compress", "None"),
    )

    button = [
        [
            InlineKeyboardButton("🪦 File Name 🪦", callback_data="ufn"),
            InlineKeyboardButton("🪦 Caption‌ 🪦", callback_data="ucp")
        ],
        [
            InlineKeyboardButton("🪦 Thumbnali 🪦", callback_data="uth"),
            InlineKeyboardButton("🪦 Regex 🪦", callback_data="uregex")
        ],
        [
            InlineKeyboardButton("⚒ Banner ⚒", callback_data="ubn"),
            InlineKeyboardButton("⚒ Compress ⚒", callback_data="u_compress"),
        ],
        [
            InlineKeyboardButton("⚙️ Password ⚙️", callback_data="upass"),
            InlineKeyboardButton("⚙️ Megre Size ⚙️", callback_data="umegre")
        ],
        [
            InlineKeyboardButton("⚒ File Type ⚒", callback_data="u_file_type"),
        ],
    ]
    if not Vars.CONSTANT_DUMP_CHANNEL:
      button[-1].append(
          InlineKeyboardButton("⚒ Dump Channel ⚒", callback_data="udc"))

    button.append([InlineKeyboardButton("❄️ Close ❄️", callback_data="close")])
    if not thumbnali:
      thumbnali = random.choice(Vars.PICS)
    try:
      await message.reply_photo(thumbnali,
                                caption=txt,
                                reply_markup=InlineKeyboardMarkup(button))
    except FloodWait as err:
      await asyncio.sleep(err.value)
      await message.reply_photo(thumbnali,
                                caption=txt,
                                reply_markup=InlineKeyboardMarkup(button))
    except:
      await message.reply_photo(photo=random.choice(Vars.PICS),
                                caption=txt,
                                reply_markup=InlineKeyboardMarkup(button))

    await sts.delete()
  except Exception as err:
    logger.exception(err)
    await sts.edit(err)


@Bot.on_message(filters.command("help"))
async def help(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")

  return await message.reply(HELP_MSG)



@Bot.on_message(filters.command(["subs", "subscribes"]))
async def isubs_cmds(_, query):
  """This Is Subscribe Handler Of Message Data"""
  sts = await query.reply("<i>ㅤProcessing.....</i>")

  user_id = str(query.from_user.id)
  if user_id not in uts:
    uts[user_id] = {}
    sync()

    return await retry_on_flood(sts.edit)("<i>ㅤYou Have No Subs .... </i>")

  manga_subs = get_subs(user_id)
  if not manga_subs:
    return await retry_on_flood(sts.edit)("<i>ㅤYou Have No Subs .... </i>")

  if manga_subs is True:
    return await retry_on_flood(sts.edit)("<i>ㅤYou Have No Subs .... </i>")

  button = []

  manga_subs = manga_subs[:60]
  try:
    for data in manga_subs:
      web = check_get_web(data['url'])
      if not web:
        continue

      data['slug'] = data['url'].split("/")[-1]
      if data['slug'] == "":
        data['slug'] = data['url'].split("/")[-2]

      c = f"chs|{web.sf}{hash(data['url'])}"
      searchs[c] = (web, data)
      button.append([InlineKeyboardButton(data['title'], callback_data=c)])

    if len(manga_subs) > 60:
        button.append([InlineKeyboardButton(f">>", callback_data=f"isubs:2")])

    button.append([InlineKeyboardButton("🔥 Close 🔥", callback_data="kclose")])

    await retry_on_flood(query.reply_photo)(
         photo=random.choice(Vars.PICS),
         quote=True,
         caption="<i>Your Subs ..</i>",
         invert_media=True,
         reply_markup=InlineKeyboardMarkup(button),
    )
    await retry_on_flood(sts.delete)()
    
  except Exception as err:
    await retry_on_flood(sts.edit)(err)
    


@Bot.on_message(filters.command("search"))
@check_token_
async def search_group(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")

  if client.SHORTENER:
    if not await premium_user(message.from_user.id):
      if not verify_token(message.from_user.id):
        if not message.from_user.id in client.ADMINS:
          return await get_token(message, message.from_user.id)

  if str(message.from_user.id) not in uts:
    uts[str(message.from_user.id)] = {}
    sync()

  if "subs" not in uts[str(message.from_user.id)]:
    uts[str(message.from_user.id)]['subs'] = {}
    sync()

  try:
    txt = message.text.split(" ")[1]
  except:
    return await message.reply("<code>Format:- /search Manga </code>")
  photo = random.choice(Vars.PICS)

  try:
    await message.reply_photo(photo,
                              caption="<i>Select search Webs ...</i>",
                              reply_markup=plugins_list(),
                              quote=True)
  except ValueError:
    await message.reply_photo(photo,
                              caption="<i>Select search Webs ...</i>",
                              reply_markup=plugins_list(),
                              quote=True)


@Bot.on_message(filters.text & filters.private)
@check_token_
async def search(client, message):
  if Vars.IS_PRIVATE:
    if message.chat.id not in Vars.ADMINS:
      return await message.reply("<code>You cannot use me baby </code>")

  if str(message.from_user.id) not in uts:
    uts[str(message.from_user.id)] = {}
    sync()

  if "subs" not in uts[str(message.from_user.id)]:
    uts[str(message.from_user.id)]['subs'] = {}
    sync()

  txt = message.text
  photo = random.choice(Vars.PICS)
  button = []
  if not txt.startswith("/"):
    try:
      await message.reply_photo(photo,
                                caption="<i>Select search Webs ...</i>",
                                reply_markup=plugins_list(),
                                quote=True)
    except ValueError:
      await message.reply_photo(photo,
                                caption="<i>Select search Webs ...</i>",
                                reply_markup=plugins_list(),
                                quote=True)
