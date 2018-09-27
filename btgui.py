import sys
import threading

import tkinter as tk
from tkinter import *
from filer import *


class BTGui(tk.Frame):

    def __init__(self, first_peer, hops=2, max_peers=5, server_port=30000, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.create_widgets()
        self.set_window_location()

        self.master.title("BerryTella Filer GUI %d" % server_port)

        self.bt_peer = FilerPeer(max_peers, server_port)
        self.bind('<Destroy>', self.__on_destroy)
        host, port = first_peer.split(':')
        self.bt_peer.build_peers(host, int(port), hops=hops)
        self.update_file_list()

        t = threading.Thread(target=self.bt_peer.main_loop, args=[])
        t.start()

        self.bt_peer.start_stabilizer(self.bt_peer.check_live_peers, 3)
        self.after(3, self.on_timer)

    def create_widgets(self):
        file_frame = Frame(self)
        peer_frame = Frame(self)

        rebuild_frame = Frame(self)
        search_frame = Frame(self)
        addfile_frame = Frame(self)
        pb_frame = Frame(self)

        file_frame.grid(row=0, column=0, sticky=N + S)
        peer_frame.grid(row=0, column=1, sticky=N + S)
        pb_frame.grid(row=2, column=1)
        addfile_frame.grid(row=3)
        search_frame.grid(row=4)
        rebuild_frame.grid(row=3, column=1)

        Label(file_frame, text='Available Files').grid()
        Label(peer_frame, text='Peer List').grid()

        file_list_frame = Frame(file_frame)
        file_list_frame.grid(row=1, column=0)
        file_scroll = Scrollbar(file_list_frame, orient=VERTICAL)
        file_scroll.grid(row=0, column=1, sticky=N + S)

        self.file_list = Listbox(file_list_frame, height=5,
                                 yscrollcommand=file_scroll.set)
        # self.fileList.insert( END, 'a', 'b', 'c', 'd', 'e', 'f', 'g' )
        self.file_list.grid(row=0, column=0, sticky=N + S)
        file_scroll["command"] = self.file_list.yview

        self.fetch_button = Button(file_frame, text='Fetch',
                                   command=self.on_fetch)
        self.fetch_button.grid()

        self.add_file_entry = Entry(addfile_frame, width=25)
        self.add_file_button = Button(addfile_frame, text='Add',
                                      command=self.on_add)
        self.add_file_entry.grid(row=0, column=0)
        self.add_file_button.grid(row=0, column=1)

        self.search_entry = Entry(search_frame, width=25)
        self.search_button = Button(search_frame, text='Search',
                                    command=self.on_search)
        self.search_entry.grid(row=0, column=0)
        self.search_button.grid(row=0, column=1)

        peer_list_frame = Frame(peer_frame)
        peer_list_frame.grid(row=1, column=0)
        peer_scroll = Scrollbar(peer_list_frame, orient=VERTICAL)
        peer_scroll.grid(row=0, column=1, sticky=N + S)

        self.peer_list = Listbox(peer_list_frame, height=5,
                                 yscrollcommand=peer_scroll.set)
        # self.peerList.insert( END, '1', '2', '3', '4', '5', '6' )
        self.peer_list.grid(row=0, column=0, sticky=N + S)
        peer_scroll["command"] = self.peer_list.yview

        self.remove_button = Button(pb_frame, text='Remove',
                                    command=self.on_remove)
        self.refresh_button = Button(pb_frame, text='Refresh',
                                     command=self.on_refresh)

        self.rebuild_entry = Entry(rebuild_frame, width=25)
        self.rebuild_button = Button(rebuild_frame, text='Rebuild',
                                     command=self.on_rebuild)
        self.remove_button.grid(row=0, column=0)
        self.refresh_button.grid(row=0, column=1)
        self.rebuild_entry.grid(row=0, column=0)
        self.rebuild_button.grid(row=0, column=1)

    def set_window_location(self):
        w = 800  # width for the Tk root
        h = 650  # height for the Tk root

        # get screen width and height
        ws = self.master.winfo_screenwidth()  # width of the screen
        hs = self.master.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        # set the dimensions of the screen
        # and where it is placed
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def on_timer(self):
        self.on_refresh()
        self.after(3000, self.on_timer)

    def __on_destroy(self):
        self.bt_peer.shut_down = True

    def update_peer_list(self):
        if self.peer_list.size() > 0:
            self.peer_list.delete(0, self.peer_list.size() - 1)
        for p in self.bt_peer.get_all_peers():
            self.peer_list.insert(END, p)

    def update_file_list(self):
        if self.file_list.size() > 0:
            self.file_list.delete(0, self.file_list.size() - 1)
        for f in self.bt_peer.files:
            p = self.bt_peer.files[f]
            if not p:
                p = '(local)'
                self.file_list.insert(END, "%s:%s" % (f, p))

    def on_add(self):
        file_entry = self.add_file_entry.get()
        if file_entry.strip():
            file_name = file_entry.strip()
            self.bt_peer.add_local_file(file_name)
        self.add_file_entry.delete(0, len(file_entry))
        self.update_file_list()

    def on_search(self):
        key = self.search_entry.get()
        self.search_entry.delete(0, len(key))
        for p in self.bt_peer.get_all_peers():
            self.bt_peer.send_to_peer(p, QUERY, "%s %s 4" % (self.bt_peer.my_id, key))

    def on_fetch(self):
        sels = self.file_list.curselection()
        if len(sels) == 1:
            sel = self.file_list.get(sels[0]).split(":")
            if len(sel) > 2:
                f_name, host, port = sel
                resp = self.bt_peer.connect_and_send(host, port, FILEGET, f_name)
                if len(resp) and resp[0][0] == REPLY:
                    fd = file(f_name, 'w')
                    fd.write(resp[0][1])
                    fd.close()
                    self.bt_peer.files[f_name] = None  # because it's local now

    def on_remove(self):
        sels = self.peer_list.curselection()
        if len(sels) == 1:
            peer_id = self.peer_list.get(sels[0])
            self.bt_peer.send_to_peer(peer_id, PEERQUIT, self.bt_peer.my_id)
            self.bt_peer.remove_peer(peer_id)

    def on_refresh(self):
        self.update_peer_list()
        self.update_file_list()

    def on_rebuild(self):
        if not self.bt_peer.max_peers_reached():
            peer_id = self.rebuild_entry.get()
            self.rebuild_entry.delete(0, len(peer_id))
            peer_id = peer_id.strip()
            try:
                host, port = peer_id.split(':')
                # print "doing rebuild", peerid, host, port
                self.bt_peer.build_peers(host, port, hops=3)
            except Exception as e:
                print e

    #         for peerid in self.btpeer.getpeerids():
    #            host,port = self.btpeer.getpeer( peerid )


def main():
    if len(sys.argv) < 4:
        logging.info("Syntax: %s server-port max-peers peer-ip:port", sys.argv[0])
        sys.exit(-1)

    # server_port = int(sys.argv[1])
    max_peers = int(sys.argv[2])
    # peer_id = sys.argv[3]

    app = BTGui(first_peer="192.168.200.246:30000", max_peers=max_peers, server_port=60000)
    app.mainloop()


if __name__ == '__main__':
    main()
