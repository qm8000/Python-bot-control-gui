import tkinter as tk
from tkinter import scrolledtext, messagebox, colorchooser
import threading
import discord
from discord.ext import commands
import asyncio
from tkinter import ttk

print("""
 __  __           _           _           
|  \/  | __ _  __| | ___     | |__  _   _ 
| |\/| |/ _` |/ _` |/ _ \    | '_ \| | | |
| |  | | (_| | (_| |  __/    | |_) | |_| |
|_|  |_|\__,_|\__,_|\___|    |_.__/ \__, |
                  ___   ___   ___   |___/ 
  __ _ _ __ ___  ( _ ) / _ \ / _ \        
 / _` | '_ ` _ \ / _ \| | | | | | |       
| (_| | | | | | | (_) | |_| | |_| |       
 \__, |_| |_| |_|\___/ \___/ \___/        
    |_|                              
""")

# Global bot instance
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot_channel = None  # Global variable for the target channel


class BotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Bot Chat")

        # Token entry
        tk.Label(root, text="Bot Token:", fg="white", bg="#333333").pack(pady=5)
        self.token_entry = tk.Entry(root, show="*", width=50, fg="white", bg="#444444")
        self.token_entry.pack(pady=5)

        # Connect button
        self.connect_button = tk.Button(root, text="Connect", command=self.start_bot, fg="white", bg="#444444")
        self.connect_button.pack(pady=5)

        # Server/Channel Selection
        self.server_frame = tk.Frame(root, bg="#333333")
        self.server_frame.pack(pady=5)

        self.channel_frame = tk.Frame(root, bg="#333333")
        self.channel_frame.pack(pady=5)

        # Chat area
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=60, height=20, fg="white", bg="#333333")
        self.chat_area.pack(pady=5)

        # Message entry
        self.message_entry = tk.Entry(root, width=50, fg="white", bg="#444444")
        self.message_entry.pack(pady=5)
        self.message_entry.bind("<Return>", self.send_message)

        # Send button
        self.send_button = tk.Button(root, text="Send", command=self.send_message, fg="white", bg="#444444")
        self.send_button.pack(pady=5)

        # Settings button
        self.settings_button = tk.Button(root, text="Settings", command=self.open_settings, fg="white", bg="#444444")
        self.settings_button.pack(pady=5)

        # Discord bot attributes
        self.bot_thread = None
        self.servers = None

        # Default background color
        self.bg_color = "#333333"
        self.presence_text = "Chatting with you"
        self.update_gui_colors()

    def log_to_chat(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def start_bot(self):
        token = self.token_entry.get().strip()

        if not token:
            messagebox.showerror("Error", "Please enter a valid bot token.")
            return

        # Start the bot in a separate thread
        self.bot_thread = threading.Thread(target=self.run_bot, args=(token,))
        self.bot_thread.daemon = True
        self.bot_thread.start()
        self.log_to_chat("Connecting bot...")

    def run_bot(self, token):
        @bot.event
        async def on_ready():
            global bot_channel
            self.log_to_chat(f"Bot connected as {bot.user}")

            self.servers = [guild for guild in bot.guilds]
            self.update_server_buttons()

            # Set the bot's presence
            await bot.change_presence(activity=discord.Game(name=self.presence_text))

            # Update presence every 5 seconds
            while True:
                await asyncio.sleep(5)
                await bot.change_presence(activity=discord.Game(name=self.presence_text))

        @bot.event
        async def on_message(message):
            if message.author == bot.user:
                return

            # Log the received message
            self.log_to_chat(f"{message.author}: {message.content}")

            # Send the message to Discord if it's from the bot
            if message.author == bot.user:
                channel = bot.get_channel(bot_channel)
                if channel:
                    await channel.send(message.content)

        try:
            bot.run(token)
        except Exception as e:
            self.log_to_chat(f"Error: {e}")

    def update_server_buttons(self):
        # Clear existing buttons
        for widget in self.server_frame.winfo_children():
            widget.destroy()

        # Create buttons for each server
        for server in self.servers:
            server_button = tk.Button(
                self.server_frame,
                text=server.name,
                command=lambda s=server: self.update_channel_buttons(s),
                fg="white",
                bg="#444444"
            )
            server_button.pack(pady=2)

    def update_channel_buttons(self, server):
        # Clear existing channel buttons
        for widget in self.channel_frame.winfo_children():
            widget.destroy()

        # Create buttons for each text channel in the selected server
        for channel in server.channels:
            if isinstance(channel, discord.TextChannel):
                channel_button = tk.Button(
                    self.channel_frame,
                    text=channel.name,
                    command=lambda c=channel: self.select_channel(c),
                    fg="white",
                    bg="#444444"
                )
                channel_button.pack(pady=2)

    def select_channel(self, channel):
        global bot_channel
        if isinstance(channel, discord.TextChannel):
            bot_channel = channel.id
            self.log_to_chat(f"Channel selected: {channel.name}")
            self.log_to_chat("Chat logs:")
        else:
            self.log_to_chat("Error: Selected item is not a text channel.")

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if not message:
            return

        self.log_to_chat(f"You: {message}")
        self.message_entry.delete(0, tk.END)

        # Send message to the target Discord channel
        if bot.is_ready() and bot_channel:
            channel = bot.get_channel(bot_channel)
            if channel:
                # Send the message asynchronously
                asyncio.run_coroutine_threadsafe(channel.send(message), bot.loop)
            else:
                self.log_to_chat("Error: Channel not found or bot not connected to it.")
        else:
            self.log_to_chat("Error: Bot is not ready or channel is not set.")

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")

        # Background color selection
        def choose_bg_color():
            color = colorchooser.askcolor(title="Choose Background Color")[1]
            if color:
                self.bg_color = color
                self.update_gui_colors()

        bg_color_label = tk.Label(settings_window, text="Background Color:", fg="white", bg="#333333")
        bg_color_label.pack(pady=5)
        bg_color_button = tk.Button(settings_window, text="Choose Color", command=choose_bg_color, fg="white", bg="#444444")
        bg_color_button.pack(pady=5)

        # Presence text entry
        def update_presence():
            self.presence_text = presence_entry.get()
            if bot.is_ready():
                asyncio.run_coroutine_threadsafe(bot.change_presence(activity=discord.Game(name=self.presence_text)), bot.loop)

        presence_label = tk.Label(settings_window, text="Presence Text:", fg="white", bg="#333333")
        presence_label.pack(pady=5)
        presence_entry = tk.Entry(settings_window, fg="white", bg="#444444")
        presence_entry.pack(pady=5)
        presence_entry.insert(0, self.presence_text)
        update_presence_button = tk.Button(settings_window, text="Update Presence", command=update_presence, fg="white", bg="#444444")
        update_presence_button.pack(pady=5)

    def update_gui_colors(self):
        self.root.config(bg=self.bg_color)
        self.chat_area.config(bg=self.bg_color)
        self.token_entry.config(bg="#444444", fg="white")
        self.connect_button.config(bg="#444444", fg="white")
        self.message_entry.config(bg="#444444", fg="white")
        self.send_button.config(bg="#444444", fg="white")
        self.settings_button.config(bg="#444444", fg="white")


# Initialize the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = BotApp(root)
    root.mainloop()
