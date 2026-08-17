from instagrapi import Client

cl = Client()

cl.login("San_dh_ya", "AYUSH212169")

username = "sanch_u1345"

user_id = cl.user_id_from_username(username)
cl.user_follow(user_id)

print(f"Successfully followed {username}")