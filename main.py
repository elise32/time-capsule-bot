import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands, Intents, Message, Interaction, Member, Guild, Role, TextChannel, Thread

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents: Intents = Intents.default()
intents.message_content = True

client: commands.Bot = commands.Bot(command_prefix='!@#$%^&*()_+', intents=intents)

class TargetHolder:
    def __init__(self) -> None:
        self.role: Role = None
        self.channel: TextChannel | Thread = None

target_holder = TargetHolder()

@client.event
async def on_ready() -> None:
    await client.tree.sync()
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    if message.author.bot:
        return
    if target_holder.role is None or target_holder.channel is None:
        return
    if message.channel.id != target_holder.channel.id:
        return
    print(f"Adding role to {message.author.name}")
    await message.author.add_roles(target_holder.role, reason="Time capsule 2024")

@client.event
async def on_message_delete(message: Message) -> None:
    if message.author == client.user:
        return
    if message.author.bot:
        return
    if target_holder.role is None or target_holder.channel is None:
        return
    if message.channel.id != target_holder.channel.id:
        return
    print(f"Removing role from {message.author.name}")
    await message.author.remove_roles(target_holder.role, reason="Time capsule 2024")

@client.tree.command(name='info', description='Shows info')
async def info(interaction: Interaction) -> None:
    role_name = target_holder.role.name if target_holder.role else None
    role_id = target_holder.role.id if target_holder.role else None
    role_mention = (' ' + target_holder.role.mention) if target_holder.role else ''
    channel_name = target_holder.channel.name if target_holder.channel else None
    channel_id = target_holder.channel.id if target_holder.channel else None
    channel_link = (f' https://discord.com/channels/{target_holder.channel.guild.id}/{target_holder.channel.id}') if target_holder.channel else ''
    await interaction.response.send_message(content=
                                                f'Role: {role_name} - {role_id}{role_mention}\n'
                                                + f'Channel: {channel_name} - {channel_id}{channel_link}'
                                            , ephemeral=True)

@client.tree.command(name='setchannel', description='Sets id of channel to listen to')
@app_commands.describe(channel_id = "The ID of the channel")
async def set_channel(interaction: Interaction, channel_id: str) -> None:
    await interaction.response.send_message(content=f'Fetching...', ephemeral=True)
    result = await fetch_channel(channel_id, interaction.guild_id)
    if result is None:
        await interaction.followup.send(content=f'Set channel failed, keeping old value of {target_holder.channel}', ephemeral=True)
    else:
        await interaction.followup.send(content=f'Set channel to {result.name} - {result.id} https://discord.com/channels/{result.guild.id}/{result.id}', ephemeral=True)

@client.tree.command(name='setrole', description='Sets id of role to assign/unassign')
@app_commands.describe(role_id = "The ID of the role")
async def set_role(interaction: Interaction, role_id: str) -> None:
    await interaction.response.send_message(content=f'Fetching...', ephemeral=True)
    result = await fetch_role(role_id, interaction.guild_id)
    if result is None:
        await interaction.followup.send(content=f'Set role failed, keeping old value of {target_holder.role}', ephemeral=True)
    else:
        await interaction.followup.send(content=f'Set role to {result.name} - {result.id} {result.mention}', ephemeral=True)

async def fetch_role(role_id: str, guild_id) -> Role | None:
    guild = await client.fetch_guild(guild_id)
    roles = await guild.fetch_roles()
    target_role = next((role for role in roles if str(role.id) == role_id), None)
    if target_role is not None:
        target_holder.role = target_role
        return target_role
    return None

async def fetch_channel(channel_id: str, guild_id) -> TextChannel | Thread | None:
    guild = await client.fetch_guild(guild_id)
    try:
        target_channel = await guild.fetch_channel(channel_id)
        target_holder.channel = target_channel
        return target_channel
    except:
        return None

def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()
