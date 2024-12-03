from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path, PurePosixPath
from time import sleep
from oneplus import oneplus
from rich.status import Status
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from PIL import Image
from utils import log
import uiautomator2 as u2


class resourceIds(Enum):
    followers_count        = "com.instagram.android:id/row_profile_header_textview_followers_count"
    following_count        = "com.instagram.android:id/row_profile_header_textview_following_count"
    profile_picture        = "com.instagram.android:id/row_profile_header_imageview"
    profile_picture_alt    = "com.instagram.android:id/profilePic"
    profile_title          = "com.instagram.android:id/action_bar_title"
    verified_badge         = "com.instagram.android:id/action_bar_title_verified_badge"

    follow_list_title      = "com.instagram.android:id/follow_list_username"
    follow_list_container  = "com.instagram.android:id/follow_list_container"
    follow_list_indicator  = "com.instagram.android:id/follow_list_row_large_follow_button"

    post_liked_stub        = "com.instagram.android:id/row_feed_like_more_info_stub"
    post_liked_count       = "com.instagram.android:id/row_feed_textview_likes"
    liked_list_container   = "com.instagram.android:id/row_user_container_base"
    liked_list_title       = "com.instagram.android:id/row_user_primary_name"
    liked_list_indicator   = "com.instagram.android:id/row_follow_button"
    reels_likes_banner     = "Plays & likes"
    reels_likes_banner_alt = "Plays and reactions"

    message_box            = "com.instagram.android:id/message_content"
    message_box_avatar     = "com.instagram.android:id/avatar"
    message_box_title      = "com.instagram.android:id/title"



@dataclass
class Profile:
    title     : str
    followers : int
    following : int
    verified  : bool

    def __init__(self) -> None:
        try:
            self.title = oneplus(resourceIds.profile_title).get_text()
            self.followers = self.get_formatted_count(resourceIds.followers_count)
            self.following = self.get_formatted_count(resourceIds.following_count)
            self.verified = any(oneplus(resourceIds.verified_badge))
        except u2.UiObjectNotFoundError:
            log.error("Timeout reached while generating profile. Please check device screen.")
    
    def get_formatted_count(self, resourceId: resourceIds) -> int:
        data: str = oneplus(resourceId).get_text()
        data = data.replace(",","")
        if "K" in data:
            data = float(data[:-1]) * 1_000
        elif "M" in data:
            data = float(data[:-1]) * 1_000_000
        return int(data)
    
    def get_profile_picture_element(self) -> tuple[u2.UiObject, bool]:
        while True:
            original  = list(oneplus(resourceIds.profile_picture))
            alternate = list(oneplus(resourceIds.profile_picture_alt))
            if original:
                element = original[0]
                alt = False
                return element, alt
            elif alternate:
                element = alternate[0]
                alt = True
                return element, alt
            else:
                sleep(1)    

    def generate_report(self, save: bool = False) -> Image.Image:
        my_insta_dir = PurePosixPath("/storage/emulated/0/Pictures/MyInsta")
        # fetch profile page
        dst_pp = Path(f"{self.title}_profile_page.jpg")
        oneplus.screenshot(str(dst_pp))
        profile_page = Image.open(dst_pp)
        # fetch profile picture
        oneplus.clean_dir(my_insta_dir)
        profile_picture, alt = self.get_profile_picture_element()
        try:
            profile_picture.long_click(duration=1)
        except u2.UiObjectNotFoundError:
            sleep(2)
            profile_picture, alt = self.get_profile_picture_element()
            profile_picture.long_click(duration=1)
        start, wait, retry = datetime.now(), 60, 10
        oneplus.long_click()
        while True:
            # wait until insta downloads profile picture for `wait` seconds | retry every 10 seconds 
            sleep(1)
            current = (datetime.now() - start).seconds
            if oneplus.count_dir(my_insta_dir) != 0:
                if int(oneplus.shell(f"find {my_insta_dir} -type f -exec stat --format '%s' {{}} +").output.splitlines()[0]):
                    break
            if current % retry == 0:
                if alt:
                    oneplus.push("Profiles/no_dp.jpg", str(my_insta_dir))
                    oneplus(description="Options").click()
                else:
                    oneplus.long_click()
            if current >= wait:
                log.error("Time limit exceeded while downloading profile picture")
        src_dp = oneplus.list_dir(my_insta_dir)[0]
        dst_dp = Path(f"{self.title}_profile_picture.jpg")
        oneplus.pull(src_dp, str(dst_dp))
        oneplus.press("back")
        # scale profile picture
        try:
            profile_picture = Image.open(dst_dp)
            report_height: int = max(profile_picture.height, profile_page.height)
            scale_factor = report_height / profile_picture.height
            profile_picture = profile_picture.resize((int(profile_picture.width*scale_factor), int(profile_picture.height*scale_factor)))
        except Exception:
            if oneplus.list_dir(my_insta_dir):
                oneplus.pull(src_dp, str(dst_dp))
                profile_picture = Image.open(dst_dp)
                profile_picture = profile_picture.resize((int(profile_picture.width*scale_factor), int(profile_picture.height*scale_factor)))
            else:
                log.error("Failed to fetch profile picture")
        # generate report image
        report_width: int = profile_picture.width + profile_page.width
        report = Image.new("RGB", (report_width, report_height))
        report.paste(profile_picture, (0,0))
        report.paste(profile_page, (profile_picture.width, 0))
        # cleanup
        oneplus.clean_dir(my_insta_dir)
        dst_dp.unlink(missing_ok=True)
        dst_pp.unlink(missing_ok=True)
        # return or save
        if save:
            report_dst = Path(f"Profiles/Users/{self.title}.jpg")
            report.save(report_dst, optimize=True)
        else:
            return report
    
    def download_profile_picture(self):
        ...


@dataclass
class Follower(Profile):
    title: str
    follow: str
    element: u2.UiObject

    def __init__(self, element: u2.UiObject) -> None:
        self.element: u2.UiObject = element
        self.followers = 0
        self.following = 0
        self.verified  = False
        self.get_attributes()
    
    def get_attributes(self) -> None:
        try:
            self.title = self.element.child(resourceId=resourceIds.follow_list_title.value).get_text(timeout=1)
            self.follow = self.element.child(resourceId=resourceIds.follow_list_indicator.value).get_text(timeout=1)
        except Exception:
            self.title = ""
            self.follow = ""
    
    def generate_profile(self) -> None:
        self.element.click()
        super().__init__()


@dataclass
class Liked_User(Follower):
    def __init__(self, element: u2.UiObject) -> None:
        super().__init__(element)
    
    def get_attributes(self) -> None:
        try:
            self.title = self.element.child(resourceId=resourceIds.liked_list_title.value).get_text(timeout=1)
            self.follow = self.element.child(resourceId=resourceIds.liked_list_indicator.value).get_text(timeout=1)
        except Exception:
            self.title = ""
            self.follow = ""

@dataclass
class Saved_User(Follower):
    is_profile: bool

    def __init__(self, element: u2.UiObject) -> None:
        self.follow = "Follow"
        self.is_profile = False
        super().__init__(element)
    
    def get_attributes(self) -> None:
        try:
            self.title = self.element.child(resourceId=resourceIds.message_box_title.value).get_text(timeout=1)
        except Exception:
            self.title = ""
    
    def generate_profile(self) -> None:
        self.element.click()
        start = datetime.now()
        while True:
            if list(oneplus(resourceIds.post_liked_stub)) or list(oneplus(resourceIds.post_liked_count)):
                oneplus.press("back")
                break
            elif list(oneplus(resourceIds.followers_count)): 
                oneplus.press("back")
                self.is_profile = True
                return super().generate_profile()
            else:
                current = datetime.now()
                if (current - start).seconds > 10:
                    oneplus.press("back")
                    break
                    

            
class Instagram:
    def __init__(self) -> None:
        self.profiles_dir      : Path = Path("./Profiles")
        self.users_dir         : Path = self.profiles_dir / "Users"
        self.scanned_users_file: Path = self.profiles_dir / "scanned.users"

        self.profiles_dir.mkdir(exist_ok=True)
        self.users_dir.mkdir(exist_ok=True)
        self.scanned_users_file.touch(exist_ok=True)
        self.get_scanned_users()
    
    def execute(self) -> None:
        if list(oneplus(resourceIds.followers_count)):
            self.followers_from_profile()
        elif list(oneplus(resourceIds.post_liked_stub)) or list(oneplus(resourceIds.post_liked_count)):
            self.liked_users_from_post()
        elif 'Like number is' in oneplus.dump_hierarchy():
            self.liked_users_from_reel()
        elif list(oneplus(resourceIds.message_box)):
            self.saved_users_from_chat()

    def followers_from_profile(self) -> None:
        with Status("Generating profile report"):
            # create a profile instance & a save dir for followers
            self.profile = Profile()
            self.save_dir = self.users_dir / self.profile.title
            self.save_dir.mkdir(exist_ok=True)
            log.info(str(self.profile))
            # generate profile report
            report_path = self.save_dir / f"{self.profile.title}.jpg"
            if not report_path.exists():
                report = self.profile.generate_report()
                report.save(report_path, optimize=True)
            self.update_scanned_users(self.profile.title)
            print()
        # sort scanned list file & close
        self.start_scanning_user()
        self.close_scanned_users()
    
    def liked_users_from_post(self) -> None:
        log.info("Getting liked users from a post\n")
        stub = list(oneplus(resourceIds.post_liked_stub))
        count = list(oneplus(resourceIds.post_liked_count))
        if stub:
            stub[0].click()
        elif count:
            count[0].click()
        else:
            log.error("Didn't find liked element to click")
        log.info("Opening the liked users list")
        self.liked_users_scan()
    
    def liked_users_from_reel(self) -> None:
        log.info("Getting liked users from a reel\n")
        hierarchy = oneplus.dump_hierarchy().splitlines()
        content_tag = list(filter(lambda x: 'Like number is' in x, hierarchy))[0]
        if content_tag:
            log.info("Opening the liked users list")
            tag_data = content_tag.split('"')
            content_desc = tag_data[tag_data.index(" content-desc=")+1]
            oneplus(description=content_desc).click()
            reels_banner = self.get_reels_banner_element()
            reels_banner.drag_to(0, 0)
        else:
            log.error("Didn't find liked element to click")
        self.liked_users_scan()
    
    def saved_users_from_chat(self) -> None:
        def scroll_inverse(only_last: bool = False):
            current_batch = list(oneplus(resourceIds.message_box))
            try:
                sx, ex = [oneplus.info["displayWidth"] // 2] * 2
                sy = current_batch[0].info["visibleBounds"]["top"]
                ey = current_batch[-1].info["visibleBounds"]["top"]
                if only_last:
                    profile_msgs = list(filter(lambda x: list(x.child(resourceId=resourceIds.message_box_avatar.value)), all_msgs))
                    if profile_msgs:
                        sy = profile_msgs[-2].info["visibleBounds"]["top"]
                oneplus.swipe_points([[sx,sy],[ex,ey]], duration=1)
            except Exception:
                if list(oneplus(text="OK")):
                    oneplus(text="OK").click()
                    scroll_inverse(only_last)
                else:
                    log.error("Failed to scroll chat")

        
        def unsend_user(msg: Saved_User) -> None:
            msg.element.long_click()
            oneplus(text="Unsend").click()

        log.info("Getting saved users from a chat\n")
        self.save_dir = self.users_dir / "Saved_users"
        self.save_dir.mkdir(exist_ok=True)
        progress_columns = [SpinnerColumn(),TextColumn("[green]Scanning"),BarColumn(),TextColumn("{task.percentage:>3.0f}%"),TimeRemainingColumn(),TextColumn("{task.description}")]
        progress = Progress(*progress_columns)
        progress.start()
        count = 100
        task = progress.add_task("Scanning...", total=count)

        log.info("Started scanning")
        index = 0
        while True:
            self.remove_post_unavailable_msgs()
            all_msgs = list(oneplus(resourceIds.message_box))
            profile_msgs = list(filter(lambda x: list(x.child(resourceId=resourceIds.message_box_avatar.value)), all_msgs))
            if profile_msgs:
                saved_user = Saved_User(profile_msgs[-1])
                index += 1
                progress.update(task, advance=1, description=f"[purple]{saved_user.title} [yellow]{index}/{count}")
                saved_user.generate_profile()
                if not saved_user.is_profile:
                    scroll_inverse(only_last=True)
                    continue
                if not saved_user.verified:
                    report = saved_user.generate_report()
                    save_path = self.save_dir / f"{saved_user.title}.jpg"
                    report.save(save_path, optimize=True)
                oneplus.press("back")
                unsend_user(saved_user)
                self.update_scanned_users(saved_user.title)
            else:
                scroll_inverse()
            
    def liked_users_scan(self) -> None:
        def wait():
            while not list(oneplus(resourceIds.liked_list_container)):
                sleep(1)
        
        def scroll(current_batch):
            sx, ex = [oneplus.info["displayWidth"] // 2] * 2
            sy = current_batch[-1].info["visibleBounds"]["top"]
            ey = current_batch[0].info["visibleBounds"]["top"]
            oneplus.drag(sx,sy,ex,ey,duration=1)
        
        wait()
        self.count_file = self.profiles_dir / "post.count"
        self.save_dir = self.users_dir / "Liked_users"
        self.save_dir.mkdir(exist_ok=True)
        progress_columns = [SpinnerColumn(),TextColumn("[green]Scanning"),BarColumn(),TextColumn("{task.percentage:>3.0f}%"),TimeRemainingColumn(),TextColumn("{task.description}")]
        progress = Progress(*progress_columns)
        progress.start()
        count = self.get_count()
        task = progress.add_task("Scanning...", total=count)

        log.info("Started scanning")
        current_set = set()
        last_user = None
        index = 0
        while True:
            current_batch: list[u2.UiObject] = list(oneplus(resourceIds.liked_list_container))
            if last_user == Liked_User(current_batch[-1]).title:
                break
            for element in current_batch:
                liked_user = Liked_User(element)
                if (liked_user.title in current_set):
                    continue
                else:
                    index += 1
                    progress.update(task, advance=1, description=f"[purple]{liked_user.title} [yellow]{index}/{count}")
                if (liked_user.title in self.scanned_users) or (liked_user.follow != "Follow"):
                    pass
                else:
                    liked_user.generate_profile()
                    if not liked_user.verified:
                        report = liked_user.generate_report()
                        save_path = self.save_dir / f"{liked_user.title}.jpg"
                        report.save(save_path, optimize=True)
                    oneplus.press("back")
                self.update_scanned_users(liked_user.title)
                if liked_user.title not in current_set:
                    current_set.add(liked_user.title)
            if liked_user.title:
                last_user = liked_user.title
            scroll(current_batch)

        progress_columns[1] = TextColumn("[green]Completed")
        progress.columns = progress_columns
        progress.update(task, advance=1, description=f"[purple]{liked_user.title} [yellow]{index}/{count}")
        progress.stop()
        self.update_count(index)
        self.close_scanned_users()

    def start_scanning_user(self) -> None:
        def open() -> None:
            if self.profile.following < self.profile.followers:
                log.info(f"Opening {self.profile.title}'s following list")
                fl_list = resourceIds.following_count
            else:
                log.info(f"Opening {self.profile.title}'s followers list")
                fl_list = resourceIds.followers_count
            oneplus(fl_list).click()
            wait()

        def wait():
            while not list(oneplus(resourceIds.follow_list_container)):
                sleep(1)

        def stop():
            return list(oneplus(text="Suggested for you"))
        
        def scroll(current_batch):
            sx, ex = [oneplus.info["displayWidth"] // 2] * 2
            sy = current_batch[-1].info["visibleBounds"]["top"]
            ey = current_batch[0].info["visibleBounds"]["top"]
            oneplus.drag(sx,sy,ex,ey,duration=1)
        
        self.count_file = self.profiles_dir / "profile.count"
        progress_columns = [SpinnerColumn(),TextColumn("[green]Scanning"),BarColumn(),TextColumn("{task.percentage:>3.0f}%"),TimeRemainingColumn(),TextColumn("{task.description}")]
        progress = Progress(*progress_columns)
        progress.start()
        count = self.get_count()
        task = progress.add_task("Scanning...", total=count)

        open()
        log.info("Started scanning")
        current_set = set()
        last_batch = False
        index = 0
        while not last_batch:
            if stop():
                last_batch = True
            current_batch: list[u2.UiObject] = list(oneplus(resourceIds.follow_list_container))
            for element in current_batch:
                follower = Follower(element)
                if (follower.title in current_set):
                    continue
                else:
                    index += 1
                    progress.update(task, advance=1, description=f"[purple]{follower.title} [yellow]{index}/{count}")
                if (follower.title in self.scanned_users) or (follower.follow != "Follow"):
                    pass
                else:
                    follower.generate_profile()
                    if not follower.verified:
                        report = follower.generate_report()
                        save_path = self.save_dir / f"{follower.title}.jpg"
                        report.save(save_path, optimize=True)
                    oneplus.press("back")
                self.update_scanned_users(follower.title)
                if follower.title not in current_set:
                    current_set.add(follower.title)
            scroll(current_batch)

        progress_columns[1] = TextColumn("[green]Completed")
        progress.columns = progress_columns
        progress.update(task, advance=1, description=f"[purple]{follower.title} [yellow]{index}/{count}")
        progress.stop()
        self.update_count(index)
    
    def remove_post_unavailable_msgs(self) -> None:
        while list(oneplus(text="Post unavailable")):
            delete_batch: list[u2.UiObject] = list(oneplus(text="Post unavailable"))
            if delete_batch:
                element = delete_batch[0]
                try:
                    element.long_click()
                    oneplus(text="Unsend").click()
                except Exception:
                    return
            else:
                if list(oneplus(text="OK")):
                    oneplus(text="OK").click()
                break

    def get_reels_banner_element(self) -> u2.UiObject:
        while True:
            original  = list(oneplus(text=resourceIds.reels_likes_banner.value))
            alternate = list(oneplus(text=resourceIds.reels_likes_banner_alt.value))
            if original:
                element = original[0]
                return element
            elif alternate:
                element = alternate[0]
                return element
            else:
                sleep(1)


    def get_scanned_users(self):
        with open(self.scanned_users_file, "r") as f:
            self.scanned_users = set(f.read().splitlines())
        self.scanned_users_writer = open(self.scanned_users_file, "a")
    
    def update_scanned_users(self, user):
        self.scanned_users.add(user)
        self.scanned_users_writer.write(f"{user}\n")
        self.scanned_users_writer.flush()
    
    def close_scanned_users(self):
        self.scanned_users_writer.close()
        with open(self.scanned_users_file,"w") as f:
            f.write("\n".join(sorted(self.scanned_users) + [""]))
    
    def get_count(self) -> int:
        with open(self.count_file,'r') as f:
            data = f.read().splitlines()
        try:
            data = list(map(int, data))
            return round(sum(data) / len(data))
        except Exception:
            return 100

    def update_count(self, count):
        with open(self.count_file, "a") as f:
            f.write(f"{count}\n")