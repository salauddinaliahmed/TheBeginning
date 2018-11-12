import tkinter, requests

class Window(tkinter.Frame):
    def __init__(self, master = None):
        tkinter.Frame.__init__(self, master)
        self.master = master
        self.init_window()
        
    def init_window(self):
        self.master.title("Weather app")
        self.grid()
        refresh_button = tkinter.Button(text = "Refresh Forcast", width =5, command = self.refresh_weather, height=2, font = ("Helvetica", 10))
        refresh_button.grid()

        exit_app = tkinter.Button(text="Exit", width=5, command = self.exit_window, height= 2, font = ("Helvetica", 10))
        exit_app.place(x =100, y =350)
        


    def refresh_weather(self):
        url = "https://api.openweathermap.org/data/2.5/weather?q=Ottawa,ca&units=metric&appid=93e8e1e020075064055fd2df87fdcebb"
        resp = requests.get(url)
        stuff = resp.json()
        temp = stuff['main']['temp']
        desc = stuff['weather'][0]['description']
        forc = stuff['weather'][0]['main']
        wind_spd = stuff['wind']['speed']
        temperature = tkinter.Label(root, text = "Temperature :" +str(temp)+ " Degree Celcius", font = ("Helvetica", 12), fg= 'red')
        description = tkinter.Label(root, text = "Sky: " + str(desc), font = ("Helvetica", 12))
        forcast = tkinter.Label(root, text = "Forcast: " + str(forc), font = ("Helvetica", 12))
        wind = tkinter.Label(root, text = "Wind Speed: " + str(wind_spd) + " Km/hr", font = ("Helvetica", 12))
        temperature.grid(column=0, row = 20)
        description.grid(column=0, row = 25)
        forcast.grid(column=0, row = 30)
        wind.grid(column = 0, row = 35)

    def exit_window(self):
        exit()

        


# canvas.pack()
# img = PhotoImage(file="/Users/salauddinali/Desktop/Adam Teav/Sports Medicine.jpeg")
# canvas.create_image(0,0, anchor=NW, image=img)
root = tkinter.Tk()
#root.geometry("480x360")
root.attributes('-fullscreen',True)
app = Window(root)
root.mainloop()
