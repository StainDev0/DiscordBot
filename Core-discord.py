import discord
from discord.ext import commands, tasks
import asyncio
from discord.ext.commands import has_permissions
from discord.ui import Button, View, Select
import random
import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
intents.messages = True
intents.bans = True
#   Najpierw napierdolimy importów i intentów by wyglądało profesionalnie

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():  
    print(f'Zalogowany jako {bot.user.name}')
    game = discord.Game(name="realmweb.pl")
    await bot.change_presence(status=discord.Status.online, activity=game)

@bot.command()
@has_permissions(kick_members=True)
async def say(ctx, *, message):  #Komenda say
    
    sent_message = await ctx.send(message)
    
    
    await asyncio.sleep(1)
    
    
    await ctx.message.delete()

@bot.command()
@has_permissions(kick_members=True)
async def embed(ctx, title, *, content):  #Komenda embed
    
    embed = discord.Embed(title=title, description=content, color=0x23a6ad)

    
    await ctx.send(embed=embed)

    
    await asyncio.sleep(1)
    await ctx.message.delete()


@bot.command()
@has_permissions(kick_members=True)
async def clear(ctx, limit: int): #Komenda Clear
    if limit < 1:
        await ctx.send("Podaj poprawny limit usuwania.")
        return
    
    deleted_messages = await ctx.channel.purge(limit=limit + 1)  

    deleted_count = len(deleted_messages) - 1 
    await ctx.send(f"{deleted_count} wiadomości usunięto.")

@bot.command()
async def weryfikacja(ctx): #System weryfikacji
    
    embed = discord.Embed(title="Weryfikacja", description="Kliknij przycisk by się zweryfikować", color=discord.Color.green())
    
    
    verify_button = Button(style=discord.ButtonStyle.green, label="Zweryfikuj")
    
    # 
    async def verify_button_callback(interaction):
        member = interaction.user
        role_id = 1168294483033595964  
        role = ctx.guild.get_role(role_id)
        if role:
            await member.add_roles(role)
            await interaction.response.send_message("Zostałeś zweryfikowany!", ephemeral=True)
        else:
            await interaction.response.send_message("Błąd: Nie znaleziono roli do nadania.", ephemeral=True)
    
    verify_button.callback = verify_button_callback
    
    
    view = View()
    view.add_item(verify_button)
    
    
    await ctx.send(embed=embed, view=view)

ROLE_IDS = {
    '📱': 1168596928204918834,
    '🎁': 1168597041874751591,
    '📢': 1168596850299904001,
}

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name}')

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if message.author == bot.user and message.embeds:
        embed = message.embeds[0]
        if embed.title == "Powiadomienia" and embed.color.value == 0x3268a8:
            emoji = str(payload.emoji)
            role_id = ROLE_IDS.get(emoji)

            if role_id:
                role = discord.utils.get(guild.roles, id=role_id)
                if role:
                    await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if message.author == bot.user and message.embeds:
        embed = message.embeds[0]
        if embed.title == "Powiadomienia" and embed.color.value == 0x3268a8:
            emoji = str(payload.emoji)
            role_id = ROLE_IDS.get(emoji)

            if role_id:
                role = discord.utils.get(guild.roles, id=role_id)
                if role and role in member.roles:
                    await member.remove_roles(role)

@bot.command()
async def autorole(ctx):
    embed = discord.Embed(
        title="Powiadomienia",
        description="📱 - Ping Techniczny\n🎁 - Ping Konkursy\n📢 - Ping Update",
        color=0x3268a8
    )

    message = await ctx.send(embed=embed)
    for emoji in ROLE_IDS.keys():
        await message.add_reaction(emoji)

@bot.command()
async def infod(ctx, member: discord.Member):
    
    statusy = {
        discord.Status.online: "Aktywny",
        discord.Status.idle: "Zaraz wracam",
        discord.Status.dnd: "Nie przeszkadzać",
        discord.Status.offline: "Niedostępny"
    }

    # Tłumaczenie statusu
    status = statusy.get(member.status, "Nieznany")

    embed = discord.Embed(title="Informacje o użytkowniku", color=discord.Color.blue())
    embed.add_field(name="Nick", value=member.display_name, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Dołączył na serwer", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Konto utworzone", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Status", value=status, inline=True)
    
    roles = [role.mention for role in member.roles[1:]]  
    if roles:
        embed.add_field(name="Role", value=" ".join(roles), inline=False)
    else:
        embed.add_field(name="Role", value="Brak ról", inline=False)

    
    top_role = member.top_role.mention
    embed.add_field(name="Najwyższa rola", value=top_role, inline=False)

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def ticket(ctx):   #System Ticketów
    category_data = {
        "1": {
            "name": "Pomoc ogólna",
            "description": "Wybierz tę kategorie jeśli chcesz otrzymać pomoc ogólną",
        },
        "2": {
            "name": "Pomoc techniczna",
            "description": "Wybierz tę kategorie jeśli chcesz dostać unbana lub backapa",
        },
        "3": {
            "name": "Zgłoś błąd",
            "description": "Wybierz tę kategorie jeśli chcesz zgłosić cheatera lub błąd",
        }
    }

    async def create_ticket(interaction):
        try:
            guild = ctx.guild
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True)
            }
            ticket_channel = await guild.create_text_channel(f'zloszenie-{interaction.user.display_name}', overwrites=overwrites)
            await ticket_channel.send(f"{interaction.user.mention}")

            close_button = discord.ui.Button(style=discord.ButtonStyle.red, label="Zamknij zgloszenie")

            async def close_ticket(interaction):
                await ticket_channel.delete()

            close_button.callback = close_ticket

            selected_category_value = interaction.data["values"][0]
            selected_category_data = category_data.get(selected_category_value, {"name": "Nieznana kategoria", "description": "Brak opisu"})

            close_embed = discord.Embed(
                title="Zgłoszenie",
                description=f"Kategoria: {selected_category_data['name']}\nOpisz swój problem, personel wkrótce zajmnie się twoją sprawą! Prosimy o cierpliwość i nie oznaczanie personelu\nKliknij poniższy przycisk, aby zamknąć ticket.",
                color=discord.Color.red()
            )

            view = discord.ui.View()
            view.add_item(close_button)

            await ticket_channel.send(embed=close_embed, view=view)
        except Exception as e:
            await interaction.response.send('Wystąpił błąd podczas tworzenia ticketu:', ephemeral=True)

    select_options = [
        discord.SelectOption(label=category_data[value]['name'], value=value)
        for value in category_data
    ]

    select = discord.ui.Select(placeholder="Wybierz kategorię", options=select_options)
    select.callback = create_ticket

    embed = discord.Embed(title="Utwórz zgłoszenie", description="Aby otrzymać pomoc od personelu, rozwiń listę poniżej wiadomości. Zostaniesz przekierowany na kanał w którym opiszesz swój problem. Prośmy o cierpliwość", color=discord.Color.green())

    view = discord.ui.View()
    view.add_item(select)

    await ctx.send(embed=embed, view=view)


@bot.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason='Brak powodu'):  
    await member.ban(reason=reason)
    await asyncio.sleep(1)
    await ctx.message.delete()
    await ctx.send(f'{ctx.author.mention} zbanował {member.mention} za: {reason}')


@bot.command()
@commands.has_permissions(kick_members=True)
async def ticketkontakt(ctx):   #System Ticketów
    category_data = {
        "1": {
            "name": "Kontakt ogólny",
            "description": "Wybierz tę kategorie jeśli chcesz otrzymać pomoc ogólną",
        },
        "2": {
            "name": "Kontakt biznesowy",
            "description": "Wybierz tę kategorie jeśli chcesz dostać unbana lub backapa",
        },
        "3": {
            "name": "Kontakt inny",
            "description": "Wybierz tę kategorie jeśli chcesz zgłosić cheatera lub błąd",
        }
    }

    async def create_ticket(interaction):
        try:
            guild = ctx.guild
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True)
            }
            ticket_channel = await guild.create_text_channel(f'zloszenie-{interaction.user.display_name}', overwrites=overwrites)
            await ticket_channel.send(f"{interaction.user.mention}")

            close_button = discord.ui.Button(style=discord.ButtonStyle.red, label="Zamknij zgloszenie")

            async def close_ticket(interaction):
                await ticket_channel.delete()

            close_button.callback = close_ticket

            selected_category_value = interaction.data["values"][0]
            selected_category_data = category_data.get(selected_category_value, {"name": "Nieznana kategoria", "description": "Brak opisu"})

            close_embed = discord.Embed(
                title="Zgłoszenie",
                description=f"Kategoria: {selected_category_data['name']}\nNapisz nam szczegóły dla czego chciałeś się z nami skontaktować oraz, napisz nazwę osoby do której kierujesz wiadomość, pamiętaj że wiadomości są moderowane!",
                color=discord.Color.red()
            )

            view = discord.ui.View()
            view.add_item(close_button)

            await ticket_channel.send(embed=close_embed, view=view)
        except Exception as e:
            await interaction.response.send('Wystąpił błąd podczas tworzenia ticketu:', ephemeral=True)

    select_options = [
        discord.SelectOption(label=category_data[value]['name'], value=value)
        for value in category_data
    ]

    select = discord.ui.Select(placeholder="Wybierz kategorię", options=select_options)
    select.callback = create_ticket

    embed = discord.Embed(title="Utwórz zgłoszenie", description="Możesz skontaktować się z kimś z rangą @Contact Me otwierając zgłoszenie. Aby to zrobić rozwiń listę poniżej i wybierz z jakiego powodu chcesz się z nami skontaktować", color=discord.Color.green())

    view = discord.ui.View()
    view.add_item(select)

    await ctx.send(embed=embed, view=view)

bot.run('Tu powienien być token')
