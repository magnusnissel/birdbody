import os
import glob
import datetime
import tkinter as tk
import tkinter.ttk as ttk
import multiprocessing as mp
import tkinter.filedialog
import tweepy
import csv
import configparser
try:
    import appdirs
except ImportError:
    import birdbody.appdirs as appdirs
HAS_PANDAS = True
try:
    import pandas as pd
except ImportError:
    HAS_PANDAS = False

 
def get_tweets_by_users(data_path, consumer_key, consumer_secret, access_key, access_secret, screen_names, conn=None):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    for sn in screen_names:
        if conn:
            msg = "Getting tweets for {} ...".format(sn)
            conn.send(msg)
        user_tweets = tweets_for_screen_name(api, sn, conn)
        if HAS_PANDAS:
            pd_user_tweets_to_csv(data_path, user_tweets, sn, conn)
        else:
            user_tweets_to_csv(data_path, user_tweets, sn, conn)
        msg = "Done with {}!".format(sn)
        if conn:
            conn.send(msg)
        else:
            print(msg) 

def tweets_for_screen_name(api, screen_name, conn=None):
    #Twitter only allows access to a users most recent 3240 tweets with this method
    #initialize a list to hold all the tweepy Tweets
    user_tweets = []  
    #make initial request for most recent tweets (200 is the maximum allowed count)
    try:
        new_tweets = api.user_timeline(screen_name = screen_name, count=200)
    except tweepy.error.TweepError as e:
        if conn:
            conn.send(e)
        else:
            print(e)
    else:
        #save most recent tweets
        user_tweets.extend(new_tweets)
        #save the id of the oldest tweet less one
        oldest = user_tweets[-1].id - 1
        #keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
            #all subsequent requests use the max_id parameter to prevent duplicates
            new_tweets = api.user_timeline(screen_name = screen_name,count=200,
                                                max_id=oldest)
            #save most recent tweets
            user_tweets.extend(new_tweets)
            #update the id of the oldest tweet less one
            oldest = user_tweets[-1].id - 1
            msg = "{} tweets downloaded for {} so far.".format(len(user_tweets), screen_name)
            if conn:
                conn.send(msg)
            else:
                print(msg)
    return user_tweets
    
    

def tweets_to_dict_list(tweets):
    today = datetime.datetime.now().date()
    tweet_dict_list = []
    for tweet in tweets:
        t = {}
        t["TWEET_ID"] = tweet.id_str
        t["CREATED"] = tweet.created_at 
        t["TEXT"] = tweet.text
        if tweet.in_reply_to_user_id:
            t["IS_REPLY"] = True
        else:
            t["IS_REPLY"] = False
        t["LANGUAGE"] = tweet.lang
        t["SCREEN_NAME"] = tweet.user.screen_name
        t["NAME"] = tweet.user.name
        t["LOCATION"] = tweet.user.location
        t["VERIFIED"] = tweet.user.verified
        t["ACCOUNT_CREATED"] = tweet.user.created_at
        t["COLLECTED"] = today
        tweet_dict_list.append(t)
    return tweet_dict_list

def pd_user_tweets_to_csv(data_path, tweets, screen_name, conn=None, add_date_to_fn=True):
    tweet_dict_list = tweets_to_dict_list(tweets)
    dn = os.path.join(data_path, "tweets", "csv")
    df = pd.DataFrame.from_dict(tweet_dict_list)
    try:
        os.makedirs(dn)
    except OSError as e:
        if e.errno != 17:
            raise()
    if not add_date_to_fn:
        fp = os.path.join(dn, "{}_tweets.csv".format(screen_name))  
    else:
        today = datetime.datetime.now().date()
        fp = os.path.join(dn, "{}_{}_tweets.csv".format(screen_name, today))
    if len(df.index) > 0:
        df.to_csv(fp)

def user_tweets_to_csv(data_path, tweets, screen_name, conn=None, add_date_to_fn=True):    
    fields = ["TWEET_ID", "CREATED", "TEXT", "IS_REPLY", "LANGUAGE", "SCREEN_NAME", "NAME", "LOCATION", 
              "VERIFIED", "ACCOUNT_CREATED", "COLLECTED"]
    tweet_dict_list = tweets_to_dict_list(tweets)
    if len(tweet_dict_list) > 0:
        dn = os.path.join(data_path, "tweets", "csv")
        try:
            os.makedirs(dn)
        except OSError as e:
            if e.errno != 17:
                raise()
        if not add_date_to_fn:
            fp = os.path.join(dn, "{}_tweets.csv".format(screen_name))  
        else:
            fp = os.path.join(dn, "{}_{}_tweets.csv".format(screen_name, today))
            today = datetime.datetime.now().date()
        with open(fp, 'w', newline='', encoding='utf8') as handler:
            writer = csv.DictWriter(handler, fieldnames=fields, dialect="excel")
            writer.writeheader()
            writer.writerows(tweet_dict_list)
            msg = "Saved tweets to {}.".format(fp)
            if conn:
                conn.send(msg)
            else:
                print(msg)


class BirdbodyGUI(tk.Frame):

    def __init__(self, root):
        tk.Frame.__init__(self)
        self.root = root
        self.default_data_path = appdirs.user_data_dir("birdbody", "Magnus Nissel")
        try:
            os.makedirs(self.default_data_path)
        except OSError as e:
            if e.errno != 17:
                raise()
        self.config_path = os.path.join(self.default_data_path, "config.ini")
        self.draw_ui()
        self.check_config()
        logo_path = "@{}".format(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                "birdbody_logo.xbm"))
        self.root.wm_iconbitmap(logo_path)
        self.root.mainloop()

    def draw_ui(self):
        self.root.title("Birdbody - Create corpora from tweets")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="news")
        self.maximize()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # --- status bar --- #
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status_var)
        self.status_bar.grid(column=0, row=1, sticky="news")
        # --- main notebook --- #
        self.book = ttk.Notebook(self)
        self.book.bind('<<NotebookTabChanged>>', self.tab_change)
        self.book.grid(column=0, row=0, sticky="news")
        self.user_tweets_frame = tk.Frame()
        self.settings_frame = tk.Frame()
        self.file_frame = tk.Frame()
        self.book.add(self.user_tweets_frame, text="Tweets by users")
        self.book.add(self.file_frame, text="File management")
        self.book.add(self.settings_frame, text="Settings")
        
        # --- settings --- #
        self.settings_frame.rowconfigure(0, weight=0)
        self.settings_frame.columnconfigure(0, weight=0)
        ttk.Label(self.settings_frame, text="Twitter API credentials",
                  font="verdana 12").grid(row=0, column=0, columnspan=2, sticky="news")
        #Twitter API credentials
        self.consumer_key_var = tk.StringVar()
        self.consumer_secret_var = tk.StringVar()
        self.access_key_var = tk.StringVar()
        self.access_secret_var = tk.StringVar()
        self.consumer_key_entry = ttk.Entry(self.settings_frame,
                                            textvariable=self.consumer_key_var, width=50)
        ttk.Label(self.settings_frame, text="Consumer key",
                  font="verdana 10").grid(row=1, column=0, sticky="news")
        self.consumer_secret_entry = ttk.Entry(self.settings_frame,
                                            textvariable=self.consumer_secret_var, width=50)
        ttk.Label(self.settings_frame, text="Consumer secret",
                  font="verdana 10").grid(row=1, column=3, sticky="news")
        self.access_key_entry = ttk.Entry(self.settings_frame,
                                            textvariable=self.access_key_var, width=50)
        ttk.Label(self.settings_frame, text="Access key",
                  font="verdana 10").grid(row=2, column=0, sticky="news")
        self.access_secret_entry = ttk.Entry(self.settings_frame,
                                            textvariable=self.access_secret_var, width=50)
        ttk.Label(self.settings_frame, text="Access secret",
                  font="verdana 10").grid(row=2, column=3, sticky="news")
        self.save_credentials_button = ttk.Button(self.settings_frame,
                                                  text="Store credentials", 
                                                  command=self.save_credentials)
        
        self.consumer_key_entry.grid(row=1, column=1, sticky="news")
        self.consumer_secret_entry.grid(row=1, column=4, sticky="news")
        self.access_key_entry.grid(row=2, column=1, sticky="news")
        self.access_secret_entry.grid(row=2, column=4, sticky="news")
        self.save_credentials_button.grid(row=3, column=0, columnspan=6, sticky="news")
        #Data path
        self.data_path_var = tk.StringVar()
        self.data_path_entry = ttk.Entry(self.settings_frame,
                                         textvariable=self.data_path_var, width=50)
        ttk.Label(self.settings_frame, text="Data path",
                  font="verdana 10").grid(row=4, column=0, sticky="news")
        self.browse_data_path_button = ttk.Button(self.settings_frame,
                                                  text="Browse", 
                                                  command=self.browse_data_path)
        self.save_data_path_button = ttk.Button(self.settings_frame,
                                                text="Store data path", 
                                                command=self.save_data_path)
        self.data_path_entry.grid(row=4, column=1, columnspan=3, sticky="news")
        self.save_data_path_button.grid(row=5, column=0, columnspan=6, sticky="news")
        self.browse_data_path_button.grid(row=4, column=4, columnspan=1, sticky="news")

        for child in self.settings_frame.winfo_children():
            try:
                child.grid_configure(padx=5, pady=5)
            except tk.TclError:
                pass
        # === user tweets === # 
        self.user_tweets_frame.rowconfigure(0, weight=1)
        self.user_tweets_frame.rowconfigure(1, weight=1)
        self.user_tweets_frame.columnconfigure(0, weight=1)
        self.user_tweets_frame.columnconfigure(1, weight=1)
        self.ut_main_frame = tk.Frame(self.user_tweets_frame)
        self.ut_main_frame.grid(row=0, column=0, sticky="news")
        self.ut_main_frame.rowconfigure(0, weight=0)
        self.ut_main_frame.rowconfigure(1, weight=1)
        self.ut_main_frame.rowconfigure(2, weight=0)
        self.ut_main_frame.rowconfigure(3, weight=0)
        self.ut_main_frame.columnconfigure(0, weight=0)
        self.ut_main_frame.columnconfigure(1, weight=0)
        self.ut_log_frame = tk.Frame(self.user_tweets_frame)
        self.ut_log_frame.rowconfigure(0, weight=0)
        self.ut_log_frame.rowconfigure(1, weight=1)
        self.ut_log_frame.columnconfigure(0, weight=1)
        self.ut_log_frame.grid(row=0, column=1, sticky="news")
        # Main
        ttk.Label(self.ut_main_frame, font="verdana 12",
                 text="Insert twitter screen names below (one per line)").grid(row=0, column=0, 
                                                                            sticky="news")
        self.screen_names_text = tk.Text(self.ut_main_frame)
        self.screen_names_text.grid(row=1, column=0, columnspan=2, sticky="news")
        
        
        self.ut_download_button = tk.Button(self.ut_main_frame,
                                         text="Download tweets", 
                                         command=self.ut_download_tweets)
        self.load_sn_button = tk.Button(self.ut_main_frame, text="Load list of names",
                                        command=self.load_screen_names)
        self.save_sn_button = tk.Button(self.ut_main_frame, text="Save list of names",
                                        command=self.save_screen_names)
        self.load_sn_button.grid(row=2, column=0, sticky="news")
        self.save_sn_button.grid(row=2, column=1, sticky="news")
        self.ut_download_button.grid(row=3, column=0, columnspan=2, sticky="news")
        # Log
        ttk.Label(self.ut_log_frame, text="Log", font="verdana 12").grid(row=0, column=0, sticky="news")
        self.ut_log_text = tk.Text(self.ut_log_frame)
        self.ut_log_text.grid(row=1, column=0, sticky="news")
        self.clear_log_button = tk.Button(self.ut_log_frame, text="Clear log",
                                          command=self.ut_clear_log)
        self.clear_log_button.grid(row=2, column=0, sticky="news")
        # Apply padding to all elements
        for child in self.user_tweets_frame.winfo_children():
            try:
                child.grid_configure(padx=5, pady=5)
            except tk.TclError:
                pass
        #=== File management frame ===#
        self.file_frame.rowconfigure(2, weight=1)
        ttk.Label(self.file_frame, font="verdana 12",
                 text="Combine CSV files or export to XML / plaintext").grid(row=0, column=0, 
                                                                 sticky="news")
        self.csv_scroll = ttk.Scrollbar(self.file_frame)
        self.csv_listbox = tk.Listbox(self.file_frame, selectmode='extended', exportselection=0, 
                                      relief="flat", yscrollcommand=self.csv_scroll.set,
                                      width=60)
        self.csv_scroll.configure(command=self.csv_listbox.yview)
        self.combine_csv_button = tk.Button(self.file_frame, text="Combine files",
                                            command=self.combine_csv_files)
        self.convert_to_xml_button = tk.Button(self.file_frame, text="Convert to .xml", command=None)
        self.convert_to_txt_button = tk.Button(self.file_frame, text="Convert to .txt", command=None)
        ttk.Label(self.file_frame, text="Filename for combination").grid(row=1, column=3,
                                                                         sticky="new")
        self.combine_csv_var = tk.StringVar()
        self.combine_csv_entry = ttk.Entry(self.file_frame,
                                           textvariable=self.combine_csv_var, width=30)
        self.csv_listbox.grid(row=2, column=0, sticky="news", rowspan=3)
        self.csv_scroll.grid(row=2, column=1, sticky="ns", rowspan=3)
        self.combine_csv_button.grid(row=2, column=2, sticky="new")
        self.convert_to_xml_button.grid(row=3, column=2, sticky="new")
        self.convert_to_txt_button.grid(row=4, column=2, sticky="new")
        self.combine_csv_entry.grid(row=2, column=3, sticky="new")
        self.file_list_dirty = True # to check if refresh is needed, e.g. after adding file

        for child in self.file_frame.winfo_children():
            try:
                child.grid_configure(padx=5, pady=5)
            except tk.TclError:
                pass


    def combine_csv_files(self):
        files = []
        udp = self.data_path_var.get().strip()
        dn = os.path.join(udp, "tweets", "csv")
        sel = self.csv_listbox.curselection()
        cfn = self.combine_csv_entry.get().replace(".csv", "").replace(".CSV", "").strip()
        if not cfn: # avoid empty filenames, eventually ask here, for now use generic fn
            now_str = str(datetime.datetime.now())
            now_str = "".join([c if c.isalnum() else "-" for c in now_str])
            cfn = "combined_tweets_{}.csv".format(now_str)
        else:
            cfn = "{}.csv".format(cfn)
        combined_path =os.path.join(dn, cfn)
        success = False
        if len(sel) > 1:
            self.update_status("Combining CSV files ...", ts=True)
            for ind in sel:
                f = self.csv_listbox.get(ind)
                fp = os.path.join(dn, f)
                files.append(fp)

            if HAS_PANDAS: # debug
                first = files[0]
                rest = files[1:]
                c_df = pd.DataFrame.from_csv(fp)
                for fp in rest:
                    df = pd.DataFrame.from_csv(fp)
                    c_df = c_df.append(df)
                c_df = c_df.drop_duplicates(subset=["TWEET_ID"])
                c_df.to_csv(combined_path)
                success = True
            else:
                all_rows = []
                fields = set()
                for fp in files:
                    with open(fp, "r") as handler:
                        reader = csv.DictReader(handler)
                        fields.update(reader.fieldnames)  # to enable compatibility if diff metadata 
                        all_rows.extend(row for row in reader)
                fields = sorted(list(fields))
                with open(combined_path, "w") as handler:
                    writer = csv.DictWriter(handler, fieldnames=fields, dialect="excel")
                    writer.writeheader()
                    writer.writerows(all_rows)
                    success = True

            if success:
                self.update_csv_file_list()
                msg = "The combined file was saved to your data folder as '{}'.".format(cfn)
                self.update_status(msg, ts=True)
            else:
                self.update_status("Sorry, there were problems combining the files.", ts=True)

            self.csv_listbox.selection_clear("0", "end")

    def save_screen_names(self):
        udp = self.data_path_var.get().strip()
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('Textfile', '.txt')]
        options['initialdir'] = os.path.join(udp, "screen_names")
        options['initialfile'] = 'screen_name_list'
        options['parent'] = self.root
        options['title'] = 'Save list of screen names'
        filepath = tk.filedialog.asksaveasfilename(**options)
        if filepath:
            sn_text = self.screen_names_text.get("0.0", "end")
            sn_text = "\n".join([sn.strip() for sn in sn_text.split("\n")])
            with open(filepath, "w") as handler:
                handler.write(sn_text)
            
    def ut_clear_log(self):
        self.ut_log_text.delete("0.0", "end")

    def load_screen_names(self):
        udp = self.data_path_var.get().strip()
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('Textfile', '.txt')]
        options['initialdir'] = os.path.join(udp, "screen_names")
        options['initialfile'] = 'screen_name_list'
        options['parent'] = self.root
        options['title'] = 'Load list of screen names'
        filepath = tk.filedialog.askopenfilename(**options)
        if filepath:
            with open(filepath, "r") as handler:
                sn_text = handler.readlines()
                sn_text = "\n".join([sn.strip() for sn in sn_text])
                self.screen_names_text.delete("0.0", "end")
                self.screen_names_text.insert("end", sn_text)
        

    def ut_download_tweets(self):
        screen_names = []
        sn_text = self.screen_names_text.get("0.0", "end")
        if sn_text:
            lines = sn_text.split("\n")
            for l in lines:
                l = l.strip()
                if l:
                    screen_names.append(l)

        if screen_names:
            udp = self.data_path_var.get().strip()
            ck = self.consumer_key_var.get().strip()
            cs = self.consumer_secret_var.get().strip()
            ak = self.access_key_var.get().strip()
            acs = self.access_secret_var.get().strip()
            #get_multi_user_tweets(udp, ck, cs, ak, acs, screen_names)
            self.ut_download_button.configure(text="Download tweets", state="disabled")
            self.main_conn, worker_conn = mp.Pipe()
            # data_path, consumer_key, consumer_secret, access_key, access_secret
            self.ut_download_worker_proc = mp.Process(target=get_tweets_by_users, args=(udp, ck, cs, ak, acs, screen_names,
                                                                                              worker_conn))
            self.ut_download_worker_proc.start()
            self.root.update()
            self.root.after(250, self.check_download_status)

            #corpus.get_multi_user_tweets(screen_names)

    def update_csv_file_list(self):
        self.csv_listbox.delete(0, "end")
        udp = self.data_path_var.get().strip()
        dn = os.path.join(udp, "tweets", "csv")
        fp = os.path.join(dn, "*.csv")
        for f in glob.iglob(fp):
            fn = os.path.basename(f)
            self.csv_listbox.insert("end", fn)

    def tab_change(self, event):
        self.tab_index = self.book.index(self.book.select())
        if self.tab_index == 1 and self.file_list_dirty:
            self.update_csv_file_list()



    def check_download_status(self):
        if not self.ut_download_worker_proc.is_alive():
            self.ut_download_worker_proc.join()
            udp = self.data_path_var.get().strip()
            op = os.path.join(udp, "tweets", "csv")
            msg = "Done downloading tweets for all users.\nTable saved to {}".format(op)
            self.file_list_dirty = True
            self.update_status(msg, ts=True)
            self.write_to_log(msg, ts=True)
            self.ut_download_button.configure(text="Download tweets", state="normal")
            self.root.update_idletasks()

        else:
            msg = self.main_conn.recv()
            if msg:
                self.update_status(msg, ts=True)
                self.write_to_log(msg, ts=True)
            self.root.update_idletasks()
            self.root.after(250, self.check_download_status)
        

    def update_status(self, text, ts=False, color=None):
        if ts:
            now = datetime.datetime.now().isoformat()[:19].replace("T"," ")
            text = "{} ({})".format(text, now)
        self.status_var.set(text)
        if color:
            self.status_bar.config(foreground=color)

    def write_to_log(self, text, ts=False):
        if ts:
            now = datetime.datetime.now().isoformat()[:19].replace("T"," ")
            text = "{} ({})".format(text, now)
        self.ut_log_text.insert("end", text)
        self.ut_log_text.insert("end", "\n")

    def save_data_path(self):
        udp = self.data_path_var.get().strip()
        if not udp:
            udp = self.default_data_path
        self.config.set("Path", "UserDataPath", udp)
        with open(self.config_path, 'w') as f:
            self.config.write(f)
        
    def save_credentials(self):
        ck = self.consumer_key_var.get().strip()
        self.config.set("Credentials", "CustomerKey", ck)
        cs = self.consumer_secret_var.get().strip()
        self.config.set("Credentials", "CustomerSecret", cs)
        ak = self.access_key_var.get().strip()
        self.config.set("Credentials", "AccessKey", ak)
        acs = self.access_secret_var.get().strip()
        self.config.set("Credentials", "AccessSecret", acs)
        with open(self.config_path, 'w') as f:
            self.config.write(f)
        
    def browse_data_path(self):
        udp = self.data_path_var.get().strip()
        p = tk.filedialog.askdirectory(initialdir=udp)
        if p:
            self.data_path_var.set(p)
            try:
                os.makedirs(p)
            except IOError as e:
                if e.errno != 17:
                    raise()

    def write_default_config(self):
        self.config.add_section("Path")
        self.config.set("Path", "UserDataPath", self.default_data_path)
        self.config.add_section("Credentials")
        self.config.set("Credentials", "CustomerKey", "")
        self.config.set("Credentials", "CustomerSecret", "")
        self.config.set("Credentials", "AccessKey", "")
        self.config.set("Credentials", "AccessSecret", "")
        with open(self.config_path, 'w') as f:
            self.config.write(f)

    def save_config(self):
        with open(self.config_path, 'w') as f:
            self.config.write(f)
            print(self.config_path)

    def check_config(self):
        self.config = configparser.SafeConfigParser()
        self.config.optionxform = str
        if not os.path.exists(self.config_path):
            self.write_default_config()
        self.config.read(self.config_path)
        ck = self.config['Credentials']['CustomerKey'].strip()
        cs = self.config['Credentials']['CustomerSecret'].strip()
        ak = self.config['Credentials']['AccessKey'].strip()
        acs = self.config['Credentials']['AccessSecret'].strip()
        udp = self.config['Path']['UserDataPath'].strip()
        if ck:
            self.consumer_key_var.set(ck)
        if cs:
            self.consumer_secret_var.set(cs)
        if ak:
            self.access_key_var.set(ak)
        if acs:
            self.access_secret_var.set(acs)
        if udp:
            self.data_path_var.set(udp)


    def book_tab_change(self, event):
        self.tab_index = self.book.index(self.book.select())


    def maximize(self):
        toplevel = self.root.winfo_toplevel()
        try:  # Windows
            toplevel.wm_state('zoomed')
        except:  # Linux
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight() - 60
            geom_string = "{}x{}+0+0".format(w, h)
            toplevel.wm_geometry(geom_string)

if __name__ == "__main__":
    mp.freeze_support()
