import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from datetime import datetime
import time
import re
import webbrowser
from urllib.parse import quote_plus

API_KEY = "API Key "  # ← Google APIキーに置き換えてください


class RouteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ルート検索アプリ")
        self.geometry("800x800")
        self.configure(bg="#f0f0f0")

        self.start_frame = StartFrame(self)
        self.search_frame = SearchFrame(self)
        self.result_frame = ResultFrame(self)

        self.start_frame.grid(row=0, column=0, sticky="nsew")
        self.search_frame.grid(row=0, column=0, sticky="nsew")
        self.result_frame.grid(row=0, column=0, sticky="nsew")

        self.start_frame.tkraise()

    def show_result(self, route_info):
        self.result_frame.display_result(route_info)
        self.result_frame.tkraise()

    def back_to_search(self):
        self.search_frame.tkraise()

    def show_search(self):
        self.search_frame.tkraise()


class StartFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ffffff")
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self, text="ルート検索アプリ", font=("Helvetica", 24, "bold"), bg="#ffffff", fg="#333")
        title.pack(pady=100)

        start_button = tk.Button(self, text="起動", font=("Helvetica", 16, "bold"),
                                 bg="#2196f3", fg="white", padx=20, pady=10,
                                 command=self.master.show_search)
        start_button.pack()


class SearchFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f0f0f0")
        self.master = master

        self.mode_var = tk.StringVar(value="driving")
        self.theme_var = tk.StringVar(value="light")

        self.create_widgets()

    def create_widgets(self):
        def section(title):
            f = tk.Frame(self, bg="white", bd=1, relief="solid", padx=10, pady=10)
            f.pack(fill="x", padx=16, pady=8)
            tk.Label(f, text=title, font=("Helvetica", 12, "bold"), bg="white").pack(anchor="w")
            return f

        loc_frame = section("出発地と目的地")
        self.origin_entry = tk.Entry(loc_frame, font=("Helvetica", 12))
        self.origin_entry.pack(fill="x", pady=4)
        self.destination_entry = tk.Entry(loc_frame, font=("Helvetica", 12))
        self.destination_entry.pack(fill="x", pady=4)

        dt_frame = section("出発日時")
        self.date_entry = tk.Entry(dt_frame, font=("Helvetica", 12))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(fill="x", pady=4)
        self.time_entry = tk.Entry(dt_frame, font=("Helvetica", 12))
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.time_entry.pack(fill="x", pady=4)

        mode_frame = section("移動手段")
        for label, value in [("🚗 車", "driving"), ("🚶 徒歩", "walking"),
                             ("🚴 自転車", "bicycling"), ("🚃 公共交通", "transit")]:
            tk.Radiobutton(mode_frame, text=label, variable=self.mode_var, value=value,
                           bg="white", font=("Helvetica", 11)).pack(anchor="w")

        theme_frame = section("地図テーマ")
        tk.Radiobutton(theme_frame, text="☀️ 昼（通常）", variable=self.theme_var, value="light",
                       bg="white", font=("Helvetica", 11)).pack(anchor="w")
        tk.Radiobutton(theme_frame, text="🌙 夜（ダーク）", variable=self.theme_var, value="dark",
                       bg="white", font=("Helvetica", 11)).pack(anchor="w")

        tk.Button(self, text="ルート検索", command=self.search_route,
                  font=("Helvetica", 14, "bold"), bg="#2196f3", fg="white").pack(pady=20)

    def search_route(self):
        origin = self.origin_entry.get()
        destination = self.destination_entry.get()
        mode = self.mode_var.get()
        theme = self.theme_var.get()

        try:
            dt_str = self.date_entry.get() + " " + self.time_entry.get()
            dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            departure_timestamp = int(time.mktime(dt_obj.timetuple()))
        except ValueError:
            messagebox.showerror("時刻エラー", "日付と時刻を正しく入力してください。")
            return

        if not origin or not destination:
            messagebox.showwarning("入力エラー", "出発地と目的地を入力してください。")
            return

        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "departure_time": departure_timestamp,
            "traffic_model": "best_guess",
            "mode": mode,
            "language": "ja",
            "key": API_KEY
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data["status"] == "OK":
                route = data["routes"][0]["legs"][0]
                steps = route["steps"]
                polyline = data["routes"][0]["overview_polyline"]["points"]
                start_loc = route["start_location"]
                end_loc = route["end_location"]

                result = {
                    "start": route["start_address"],
                    "end": route["end_address"],
                    "duration": route["duration"]["text"],
                    "distance": route["distance"]["text"],
                    "steps": steps,
                    "polyline": polyline,
                    "start_loc": start_loc,
                    "end_loc": end_loc,
                    "mode": mode,
                    "theme": theme
                }

                self.master.show_result(result)
            else:
                messagebox.showerror("APIエラー", f"Status: {data['status']}")
        except Exception as e:
            messagebox.showerror("通信エラー", str(e))


class ResultFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f0f0f0")
        self.master = master

        self.result_text = tk.Text(self, wrap=tk.WORD, font=("Helvetica", 11), height=12)
        self.result_text.pack(padx=16, pady=8, fill="both")

        self.map_label = tk.Label(self, bg="#f0f0f0")
        self.map_label.pack(pady=10)

        tk.Button(self, text="🌐 HTMLで地図を表示", command=self.open_html_map,
                  font=("Helvetica", 13), bg="#bbb").pack(pady=5)

        tk.Button(self, text="🔙 戻る", command=self.master.back_to_search,
                  font=("Helvetica", 13), bg="#ddd").pack(pady=10)

        self.current_info = None

    def display_result(self, info):
        self.current_info = info
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"【移動手段】{self.translate_mode(info['mode'])}\n")
        self.result_text.insert(tk.END, f"出発地: {info['start']}\n")
        self.result_text.insert(tk.END, f"目的地: {info['end']}\n")
        self.result_text.insert(tk.END, f"距離: {info['distance']}\n")
        self.result_text.insert(tk.END, f"所要時間: {info['duration']}\n\n")

        self.result_text.insert(tk.END, "【ルート案内】\n\n")
        for i, step in enumerate(info["steps"], start=1):
            instruction = step["html_instructions"]
            clean = re.sub(r'<[^>]+>', '', instruction)  # HTMLタグ除去
            self.result_text.insert(tk.END, f"{i}. {clean}\n\n")

        self.display_map(info["polyline"], info["start_loc"], info["end_loc"], info["theme"])

    def display_map(self, encoded_polyline, start_loc, end_loc, theme):
        style = ""
        if theme == "dark":
            style = (
                "&style=feature:all|element:geometry|color:0x242f3e"
                "&style=feature:all|element:labels.text.stroke|color:0x242f3e"
                "&style=feature:all|element:labels.text.fill|color:0x746855"
                "&style=feature:road|element:geometry|color:0x38414e"
                "&style=feature:poi|element:labels.text.fill|color:0xd59563"
            )

        map_url = (
            f"https://maps.googleapis.com/maps/api/staticmap?size=400x300"
            f"&maptype=roadmap"
            f"&markers=color:green|label:S|{start_loc['lat']},{start_loc['lng']}"
            f"&markers=color:red|label:G|{end_loc['lat']},{end_loc['lng']}"
            f"&path=enc:{encoded_polyline}{style}"
            f"&key={API_KEY}"
        )

        response = requests.get(map_url)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image = ImageTk.PhotoImage(image)

            self.map_label.config(image=image)
            self.map_label.image = image
        else:
            messagebox.showerror("地図取得失敗", "地図画像の取得に失敗しました。")

    def open_html_map(self):
        if not self.current_info:
            messagebox.showwarning("警告", "ルート情報がありません。")
            return

        origin = self.current_info["start"]
        destination = self.current_info["end"]
        mode = self.current_info["mode"]

        base_url = "https://www.google.com/maps/dir/?api=1"
        origin_enc = quote_plus(origin)
        dest_enc = quote_plus(destination)
        url = f"{base_url}&origin={origin_enc}&destination={dest_enc}&travelmode={mode}"

        webbrowser.open(url)

    def translate_mode(self, mode):
        return {
            "driving": "車",
            "walking": "徒歩",
            "bicycling": "自転車",
            "transit": "公共交通機関"
        }.get(mode, mode)


if __name__ == "__main__":
    app = RouteApp()
    app.mainloop()