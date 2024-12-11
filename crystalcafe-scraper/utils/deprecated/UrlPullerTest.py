import deprecated.UrlPuller as UrlPuller
import os

puller_file = os.path.join('URLs', 'list.txt')
puller = UrlPuller.UrlPuller(puller_file)
print("first loop")
for i in range(puller.get_size()):
    print(puller.get_url())
    puller.next_url()

puller_file_2 = os.path.join('URLs', 'list2.txt')
puller.set_new_file_list(puller_file_2)
print("second loop")
for i in range(puller.get_size()):
    print(puller.get_url())
    puller.next_url()
