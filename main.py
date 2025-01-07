import uiautomator2 as u2
import time,os, random,requests
from dotenv import load_dotenv

#359.0.0.59.89

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in environment variables or .env file")

def get_random_comment_from_file(filename="comments.txt"):
    try:
        with open(filename, "r") as file:
            comments = file.readlines()
        return random.choice(comments).strip()
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return "Nice post!"

def get_gpt_response(prompt, api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()
        return response_json['choices'][0]['message']['content'].strip()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return get_random_comment_from_file()

def  generate_comment_from_caption(caption):
    prompt = f"""This is a caption from an Instagram post:
        "{caption}"

        Can you generate a thoughtful and engaging comment for this post? make the reply short and humanzie the answer"""
    return get_gpt_response(prompt, api_key)

def extract_caption(device):
    try:
        time.sleep(2)
        _ = device.xpath("//com.instagram.ui.widget.textview.IgTextLayoutView")
        caption = _.all()[-1]
        return caption.text
        
    except Exception as e:    
        print(f"[-] Error extracting caption: {e}")
    return None

def like_post(device):
    try:
        like_button = device(resourceId='com.instagram.android:id/row_feed_button_like')
        if like_button:
            if like_button.info['contentDescription'] == 'Liked':
                print("[+] Already liked the post")
            else:
                like_button.click()
                print("[+] Post Liked")
                return True
        else:
            print("Like button not found")
            return False
    except:
        like_button = device(resourceId='com.instagram.android:id/toolbar_like_container')
        if like_button:
            if like_button.info['contentDescription'] == 'Liked':
                print("[+] Already liked the post")
            else:
                like_button.click()
                print("[+] Post Liked")
                return True
        else:
            print("Like button not found")
            return False
    
def comment_on_location(device, hashtag, num_post, like_posts , comment_posts ) :
    if not search_hashtag(device, hashtag):
        return

    places = device(text="Places").click()
    time.sleep(3)

    res = device.xpath('//*[@resource-id="com.instagram.android:id/recycler_view"]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]').click()
    time.sleep(2)
    recent = device(text="Recent").click()
    time.sleep(6)

    index = 2 # Start index at 0
    posts_count = 0 
    while posts_count < num_post:
        try:
            time.sleep(2)
            post = device(resourceId="com.instagram.android:id/image_button", index=index)
            post.click()
            time.sleep(2)
        
            if like_posts and random.random() <= 0.7:  
                like_successful = like_post(device)
                if like_successful:
                    print("Liked post successfully")
                else:
                    print("[-] Failed to like post, swiping to next post.")
            if comment_posts and random.random() <= 0.7:  
                caption = extract_caption(device)
                print(caption)
                time.sleep(2) 
                if caption:
                    comment_text = generate_comment_from_caption(caption)
                    print(comment_text)
                    time.sleep(3)
                    comment_successful = comment_on_post(device, comment_text)
                    if comment_successful:
                        print("Commented on post successfully")
                    else:
                        print("[-] Error during commenting, swiping to next post.")
                else:
                    print("[-] Could not extract caption, swiping to next post.")
            
            device.press('back')
            time.sleep(2)
            
            # Update the index
            index += 1
            if index > 12:
                index = 0
                device.swipe(500, 1500, 500, 500)
                
            
            posts_count += 1
            print(f'Number of posts processed = {posts_count}')
        except Exception as e:
            print(f"[-] Error processing post: {e}")
            device.press('back')
            time.sleep(2)
            device.swipe(500, 1500, 500, 500)
            time.sleep(2)
            posts_count += 1
            print(f'Number of posts processed = {posts_count}')

def comment_on_post(device, comment_text):
    try:
        comment_button = device(resourceId="com.instagram.android:id/row_feed_button_comment")
        if comment_button:
            time.sleep(2)
            comment_button.click()
            time.sleep(2)
            comment_field = device(resourceId="com.instagram.android:id/layout_comment_thread_edittext")
            comment_field.set_text(comment_text)
            time.sleep(2)
            post_button = device(resourceId="com.instagram.android:id/layout_comment_thread_post_button_icon")
            post_button.click()

            print("[+] Commented on the post")
            time.sleep(2)
            device.press('back')
            time.sleep(2)
            device.press('back')
            return True
        else:
            pass
            print("Comment button not found")
    except Exception as e:
        print(f"[-] Error commenting on the post: {e}")
    return False

def search_hashtag(device, hashtag):
    device.session("com.instagram.android")
    device.sleep(4)

    search_button = device.xpath('//*[@resource-id="com.instagram.android:id/search_tab"]')
    search_button.click()
    device.sleep(4)
    
    search_bar = device.xpath('//*[@resource-id="com.instagram.android:id/action_bar_search_hints_text_layout"]')
    search_bar.click()
    # search_bar.set_text(f"#{hashtag}")
    # time.sleep(2)
    # os.system(f"adb shell input tap {36} {165}")
    time.sleep(2)
    os.system(f"adb shell input tap {852} {132}")
    time.sleep(1)
    # Step 4: Input text "Places"
    os.system(f'adb shell input text "{hashtag}"')
    time.sleep(3)
    # search_box = device(resourceId="com.instagram.android:id/action_bar_search_hints_text_layout")
    device.press("enter")

    
    # try:
    #     hashtag_result = device(resourceId="com.instagram.android:id/row_search_keyword_title", text=f"#{hashtag}")
    #     if hashtag_result:
    #         hashtag_result.click()
    #         time.sleep(2)
    #     else:
    #         hashtag_result1= device.xpath('//*[@resource-id="com.instagram.android:id/recycler_view"]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.widget.TextView[1]', text=f"#{hashtag}")
    #         if hashtag_result1:
    #             hashtag_result1.click()
    #             time.sleep(2)
    # except:
    #     print("Hashtag not found. Please try another one.")
    #     return False
    return True

def comment_on_hashtag_posts(device, hashtag, num_post, like_posts, comment_posts):
    # search_hashtag(device, hashtag)
    if not search_hashtag(device, hashtag):
        return
    
    post = device(resourceId="com.instagram.android:id/image_button", index=0)
    post.click()
    time.sleep(2)

    posts_count = 0 
    while posts_count < num_post:
        time.sleep(2)
        
        if like_posts and random.random() <= 0.6:  
            like_successful = like_post(device)
            if like_successful:
                print("Liked post successfully")
            else:
                print("[-] Failed to like post, swiping to next post.")

        if comment_posts and random.random() <= 0.6:  
            caption = extract_caption(device)
            print(caption)
            time.sleep(2) 
            if caption:
                comment_text = generate_comment_from_caption(caption)
                print(comment_text)
                time.sleep(3)
                comment_successful = comment_on_post(device, comment_text)
                if comment_successful:
                    print("Commented on post successfully")
                else:
                    print("[-] Error during commenting, swiping to next post.")
                    device.swipe(500, 1500, 500, 500)  

            else:
                print("[-] Could not extract caption, swiping to next post.")
                device.swipe(500, 1500, 500, 500)  

        time.sleep(5)
        device.swipe(500, 1500, 500, 500)  
        time.sleep(2)
        posts_count += 1
        print(f'Number of post = {posts_count}')

def comment_on_profile_followers(device, profile_username, num_users, like_posts, comment_posts, follow_profile):
    profile_url = f"instagram://user?username={profile_username}"
    print(f"[+] Opening profile: {profile_url}...........")
    device.open_url(profile_url)
    time.sleep(4)

    followers_count = device(resourceId="com.instagram.android:id/row_profile_header_textview_followers_count")
    followers_count.click()
    print("[+] Clicked on followers count.")
    time.sleep(2)

    interacted_profiles = set()  # Set to track interacted profiles

    user_count = 0
    while user_count< num_users:
        # Adjusting to find the story indicator correctly
        story_indicator = device.xpath('//*[@content-desc="@2131971163"]')

        if story_indicator.exists:
            story_indicator.click()
            time.sleep(2)
            try:
                profile_name_element = device.xpath('//*[@resource-id="com.instagram.android:id/reel_viewer_title"]')
            except:
                profile_name_element = device(resourceId="com.instagram.android:id/reel_viewer_title")


            try:
                if profile_name_element.exists:
                    profile_name = profile_name_element.get().info['text']
                    
                    # Check if we have already interacted with this profile
                    if profile_name in interacted_profiles:
                        print(f"[-] Already interacted with profile: {profile_name}")
                        # Swipe to the next story if available
                        device.press('back')
                        time.sleep(2)
                        continue
                    else:
                        profile_name_element = device.xpath('//*[@resource-id="com.instagram.android:id/reel_viewer_title"]')
                        profile_name_element.click()
                        time.sleep(3)

                        post = device(resourceId="com.instagram.android:id/media_set_row_content_identifier").child(index=0)
                        if post.exists:
                            post.click()
                            print("[+] Post found, interacting with the post.")
                            if follow_profile:
                                follow = device(text ='Follow')
                                follow.click()
                                time.sleep(4)
                                print('[+] User Followed')
                                alert= device(text='OK')
                                if alert.exists:
                                    alert.click()
                                    print('[+] ⚠️Alert Clicked')
                            else:
                                print('[-] Already Followed')
                            time.sleep(2)
                            if like_posts and random.random() <= 0.7:
                                time.sleep(2)
                                # post = device(resourceId="com.instagram.android:id/media_set_row_content_identifier").child(index=0)  
                                # post.click()
                                like_successful = like_post(device)
                                if like_successful:
                                    print("[+] Liked post successfully")
                                    # print(f'[+] The Number of user interacted with {user_count}')

                                else:
                                    print("[-] Failed to like post, swiping to next post.")

                            if comment_posts and random.random() <= 0.7:
                                try:
                                    caption = extract_caption(device)
                                    print(f'[+] Caption : {caption}')
                                    comment_text = generate_comment_from_caption(caption)
                                    print(f"[+] Generated comment: {comment_text}")
                                    time.sleep(5)
                                    comment_on_post(device, comment_text)
                                    time.sleep(2)
                                    device.press('back')
                                except Exception as e:
                                    print(f"[-] Error commenting on post: {e}")
                                 
                                time.sleep(3)
                                device.press('back')
                                time.sleep(3)
                                device.press('back')
                                time.sleep(3)
                                device.press('back')
                                user_count += 1
                                print(f'[+] The Number of user interacted with {user_count}')
                            else:
                                print('[-] Already Liked')
                                time.sleep(2)
                                device.press('back')
                                time.sleep(2)
                                device.press('back')
                                time.sleep(2)
                                device.press('back')
                        else:
                            print("[-] No posts found, going back to followers list.")
                            time.sleep(2)
                            device.press('back')
                            time.sleep(2)
                            device.press('back')
                        time.sleep(2)

                    print(f"[+] Interacting with profile: {profile_name}")
                    interacted_profiles.add(profile_name)
            except:
                pass
        else:
            # device.press('back')
            profile_share = device.xpath('//*[@content-desc="Profile Share"]')
            if profile_share.exists:
                followers_count = device(resourceId="com.instagram.android:id/row_profile_header_textview_followers_count")
                print ("[+] Clicked on followers count Again.")
                followers_count.click()
            print("[-] No stories found, swiping to look for more stories....")
            device.swipe(500, 1200, 500, 300)  # Adjust swipe coordinates as needed
            time.sleep(2)
            see_more = device.xpath('//*[@resource-id="com.instagram.android:id/see_more_button"]')
            if see_more.exists:
                print("[+] Clicking 'see more' to load more followers.")
                see_more.click()

def comment_on_home_feed(device, like_posts, comment_posts):
    device.session("com.instagram.android")
    time.sleep(2)

    while True:
        if like_posts and random.random() <= 0.6:
            like_successful = like_post(device)
        
        if comment_posts and random.random() <= 0.6:
            caption = extract_caption(device)
            comment_text = generate_comment_from_caption(caption)
            print(comment_text)
            time.sleep(4)
            comment_successful = comment_on_post(device, comment_text)
            comment_Alert= device(text='Not Now')
            if comment_Alert.exists:
                time.sleep(2)
                comment_Alert.click()
                print('Comment Alert Clicked')
            if not comment_successful:
                print("[-] Error during commenting, swiping to next post.")
        else:
            print("[-] Like button not found, swiping to next post")
        
        device.swipe(500, 1200, 500, 300)  # Swipe to next post
        print("[+] Swiping to next post")
        time.sleep(3)

def comment_on_stories(device, like_posts):
    device.session("com.instagram.android")
    time.sleep(2)

    stories = device.xpath('//*[@content-desc="reels_tray_container"]/android.widget.LinearLayout[2]/android.widget.FrameLayout[1]/android.widget.Button[1]/android.widget.FrameLayout[1]/android.view.View[1]')
    stories.click()
    time.sleep(2)
        
    print("Liking the story")
    while True:
        # try:
            like_button = device(resourceId="com.instagram.android:id/toolbar_like_container")
            if like_button:
                like_button.click()
                time.sleep(2)
                print("now swiping")
                scroll=device(resourceId='com.instagram.android:id/reel_viewer_media_layout')
                scroll.swipe("left")
                time.sleep(2)
            else:
                print("[-] Like button not found.")
                scroll=device(resourceId='com.instagram.android:id/reel_viewer_media_layout')
                scroll.swipe("left")
                time.sleep(2)
        # except Exception as e:
        #     device.press('back')
        #     time.sleep(2)
        #     print("Stories completed")
        #     break

def main():
    device = u2.connect('')
    while True:
        print("\nMenu:")
        print("1. Comment on posts related to hashtags")
        print("2. Comment on selected profile's followers and their followers")
        print("3. Comment on location/places")
        print("4. Comment on home feed")
        print("5. Comment on stories")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice in ['1', '2', '3', '4', '5']:
            like = input("Do you want to like the posts as well? (y/n): ").strip().lower()
            comment = input("Do you want to comment on the posts? (y/n): ").strip().lower()

        if choice == '1':
            hashtag = input("Enter the hashtag: ")
            num_posts = int(input("Enter the number of posts to interact with (e.g., 10, 20, 30): "))
            comment_on_hashtag_posts(device, hashtag, num_posts, like == 'y', comment == 'y')
        elif choice == '2':
            profile_username = input("Enter the profile username: ")
            num_users = int(input("Enter the number of users to interact with (e.g., 10, 20, 30): "))
            follow = input("Do you want to follow on the posts? (y/n): ").strip().lower()
            comment_on_profile_followers(device, profile_username, num_users, like == 'y', comment == 'y', follow=="y")
        elif choice == '3':
            location = input("Enter the location: ")
            loc_posts = int(input("Enter the number of posts to interact with (e.g., 10, 20, 30): "))
            comment_on_location(device, location, loc_posts, like == 'y', comment == 'y')
        elif choice == '4':
            comment_on_home_feed(device, like == 'y', comment == 'y')
        elif choice == '5':
            comment_on_stories(device, like == 'y')
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
