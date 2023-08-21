# this file containes dictionary of all texts and sentences used in app and ui, in english and farsi


ERRORS = {

        'test': {'fa':'تست',
                'en':'message'},

        'label_set_image_failed': {'fa':'خطای اختصاص تصویر به لیبل.',
                'en':'Error while setting image to label.'},

        'label_show_message_failed': {'fa':'خطای نمایش پیغام در لیبل.',
                'en':'Error while showing message on label.'},
        
        'button_set_icon_failed': {'fa':'خطای اتصال آیکون به دکمه.',
                'en':'Error while setting icon to button.'},
        
        'element_setenabled_failed': {'fa':'خطای فعال/غیر فعال سازی المان.',
                'en':'Error while enabling/disabling element.'},
        
        'sql_connect_failed': {'fa':'خطای اتصال به اس‌کیوال.',
                'en':'Error while connecting to MySQL.'},
        
        'db_load_cam_params_failed': {'fa':'خطای دریافت پارامترهای دوربین از پایگاه داده.',
                'en':'Error while recieving cameras parameters from database.'},
        
        'build_database_object_failed': {'fa':'خطای ساخت ماژول ارتباط با پایگاه داده.',
                'en':'Error while building database module.'},
        
        'initialize_modules_failed': {'fa':'خطای ساخت ماژول‌های ابتدایی نرم‌افزار، امکان اجرای نرم‌افزار وجود ندارد.',
                'en':'Error while building starting app modules, App cant be started.'},
        
        'app_force_closed': {'fa':'نرم‌افزار به صورت اجبار بسته شد، احتمالا خطایی رخ داده است.',
                'en':'App is closed by force, There may be a problem.'},
        
        'db_update_cam_params_failed': {'fa':'خطای بروزرسانی پارامترهای جدید دوربین در پایگاه داده.',
                'en':'Error while updating new cameras parameters on database.'},
        
        'database_camera_serials_update_failed': {'fa':'خطای بروزرسانی دوربین‌های در دسترس در پایگاه داده.',
                'en':'Error while updating available cameras on database.'},
        
        'camera_connect_failed': {'fa':'خطای اتصال به دوربین، احتمالا مشکلی وجود دارد.',
                'en':'Error while connecting to the camera, , There may be a problem.'},
        
        'camera_controlled_by_another_app': {'fa':'دوربین توسط نرم‌افزار دیگری در حال کنترل است، لطفا ابتدا آن را ببندید.',
                'en':'Camera is being controlling by another application, Please close it first.'},
        
        'exposure_too_low': {'fa':'مقدار اکسپوژر کمتر از حد مجاز است.',
                'en':'Exposure value is too low.'},
        
        'exposure_too_high': {'fa':'مقدار اکسپوژر بیشتر از حد مجاز است.',
                'en':'Exposure value is too high.'},
        
        'exposure_invalid': {'fa':'مقدار اکسپوژر در بازه مجاز نیست.',
                'en':'Exposure value is not in range.'},
        
        'gain_too_low': {'fa':'مقدار گین کمتر از حد مجاز است.',
                'en':'Gain value is too low.'},
        
        'gain_too_high': {'fa':'مقدار گین بیشتر از حد مجاز است.',
                'en':'Gain value is too high.'},
        
        'gain_invalid': {'fa':'مقدار گین در بازه مجاز نیست.',
                'en':'Gain value is not in range.'},
        
        'width_too_low': {'fa':'مقدار عرض کمتر از حد مجاز است.',
                'en':'Width value is too small.'},
        
        'width_too_high': {'fa':'مقدار عرض بیشتر از حد مجاز است.',
                'en':'Width value is too large.'},
        
        'width_invalid': {'fa':'مقدار عرض در بازه مجاز نیست.',
                'en':'Width value is not in range.'},
        
        'height_too_low': {'fa':'مقدار طول کمتر از حد مجاز است.',
                'en':'Height value is too small.'},
        
        'height_too_high': {'fa':'مقدار طول بیشتر از حد مجاز است.',
                'en':'Height value is too large.'},
        
        'height_invalid': {'fa':'مقدار عرض در بازه مجاز نیست.',
                'en':'Height value is not in range.'},
        
        'offsetx_too_low': {'fa':'مقدار افست عرض کمتر از حد مجاز است.',
                'en':'OffsetX value is too small.'},
        
        'offsetx_too_high': {'fa':'مقدار افست عرض بیشتر از حد مجاز است.',
                'en':'OffsetX value is too large.'},
        
        'offsetx_invalid': {'fa':'مقدار افست عرض در بازه مجاز نیست.',
                'en':'OffsetX value is not in range.'},
        
        'offsety_too_low': {'fa':'مقدار افست طول کمتر از حد مجاز است.',
                'en':'OffsetY value is too small.'},
        
        'offsety_too_high': {'fa':'مقدار افست طول بیشتر از حد مجاز است.',
                'en':'OffsetY value is too large.'},
        
        'offsety_invalid': {'fa':'مقدار افست طول در بازه مجاز نیست.',
                'en':'OffsetY value is not in range.'},
        
        'packetsize_invalid': {'fa':'مقدار سایز بسته در بازه مجاز نیست.',
                'en':'Packet size value is not in range.'},
        
        'transmision_delay_too_low': {'fa':'مقدار تاخیر انتقال کمتر از حد مجاز است.',
                'en':'Transmision delay value is too low.'},
        
        'transmision_delay_too_high': {'fa':'مقدار تاخیر انتقال بیشتر از حد مجاز است.',
                'en':'Transmision delay value is too high.'},
        
        'transmision_delay_invalid': {'fa':'مقدار تاخیر انتقال در بازه مجاز نیست.',
                'en':'Transmision delay value is not in range.'},
        
        'apply_setup_failed': {'fa':'خطای ذخیره‌سازی تنظیمات پیکربندی دستگاه.',
                'en':'Error while saving system configurations.'},
        
        'database_create_failed': {'fa':'خطای ایجاد پایگاه داده، لطفا تنظیمات اس‌کیوال را بررسی نمایید.',
                'en':'Error while creating database, please check SQL setup'},
        
        'setup_file_corrupted': {'fa':'تنظیمات پیکربندی دستگاه حذف و یا خراب شده است، لطفا مجدد پیکربندی را انجام دهید.',
                'en':'System configurations are missed or corrupted, Please set configurations again.'},
        
        'db_add_user_failed': {'fa':'خطای افزودن کاربر جدید در پایگاه داده.',
                'en':'Error while adding user to database.'},
        
        'db_update_user_info_failed': {'fa':'خطای بروزرسانی اطلاعات جدید کاربر در پایگاه داده.',
                'en':'Error while updating user new info on database.'},

        'user_info_invalid': {'fa':'اطلاعات کاربری اشتباه است.',
                'en':'User info are invalid.'},

        'user_doesnt_have_access': {'fa':'دسترسی برای این کاربر ممنوع است.',
                'en':'Access denied for this user.'},
        
        'prevent_delete_user': {'fa':'امکان حذف کاربر واردشده فعلی وجود ندارد.',
                'en':'Can not delete current logged in user.'},

        'prevent_modify_user': {'fa':'امکان اصلاح کاربر واردشده فعلی وجود ندارد.',
                'en':'Can not modify current logged in user.'},

              
}


WARNINGS = {

        'test': {'fa':'تست',
                'en':'This is a test message'},

        'load_raw_image_failed': {'fa':'خطای بارگذاری تصویر خام.',
                'en':'Failed to load raw image.'},
        
        'app_close_confirm': {'fa':'آیا نسبت به خروج از نرم‌افزار اطمینان دارد؟',
                'en':'Are you sure to close the app?'},
        
        'app_closed_change_language': {'fa':'نرم‌افزار جهت اعمال زبان جدید بسته شد.',
                'en':'App is closed to apply new language.'},
        
        'app_close_to_change_language': {'fa':'نرم‌افزار بایستی جهت اعمال زبان جدید بسته شود.',
                'en':'App must be closed to apply new lan guage.'},
        
        'app_force_close': {'fa':'نرم‌افزار بایستی بسته شود، احتمالا خطایی رخ داده است.',
                'en':'App must be closed, There may be a problem.'},

        'some_cameras_not_connected': {'fa':'دوربین به شبکه متصل نیست، لطفا مشکل را بررسی کنید.',
                'en':'The camera is not connected to the network, please check the problem.'},
        
        'db_no_camera_found_by_serial': {'fa':'هیچ دوربینی با سریال موردنظر پیدا نشد.',
                'en':'No camera was found with input camera serial.'},
        
        'cam_no_serial_assigned': {'fa':'هیچ سریالی به این دوربین اختصاص داده نشده است، لطفا ابتدا یک سریال انتخاب کنید.',
                'en':'No Serial is assigned to this camera, Please select one first.'},
        
        'camera_disconnect': {'fa':'اتصال به دوربین قطع شد.',
                'en':'Camera is disconnected.'},

        'algo_params_incorrect': {'fa':'بازه های واردشده به فرمت درست وارد نشده اند.',
                'en':'Input ranges are not entered on valid format.'},
        'calibration_file_does_not_exist': {'fa':'فایل کالیبره موجود نیست',
                'en':'Calibration file does not exist.'},
        'was_not_able_to_calibrate': {'fa':'موفق به کالیبره نشد، مقادیر قبلی استفاده می‌شود',
        'en':'Was not able to calibrate.'},

        'are_you_sure':{'fa':'آیا نسبت به افزودن بازه جدید مطمئن هستید؟',
                'en':'Are you sure about adding a new range??'},

        'are_you_sure_delete': {'fa':'آیا از حذف رکورد مطمئن هستید؟',
                'en':'Are you sure you want to delete the record?'},
        
        'are_you_sure_save_reset' : {'fa':'آیا می خواهید نتایج را ذخیره و جدول های صفحه را مجددا بارگزاری کنید؟',
                'en':'Do you want to save results and reload page tables?'},

        'are_you_sure_stop' : {'fa': 'آیا می خواهید پردازش را متوقف کنید؟',
                'en':'Are you sure stop detection?'},

        'detection_activation': {'fa':'الگوریتم تشخیص دانه بندی فعال شد.',
                'en':'The granularity detection algorithm is activated.'},

        'fields_empty': {'fa':'یک یا تعدادی از فیلدها خالی هستند، لطفا همه آنها را پر نمایید.',
            'en':'One or multiple fields are empty, Please Fill them all.'},
        
        'database_exists': {'fa':'یک پایگاه داده با این نام وجود دارد، آیا نسبت به ساخت مجدد آن اطمینان دارید؟ در اینصورت تمامی اطلاعات موجود در این پایگاه داده پاک می‌شود!',
                'en':'There is a database with this name, Are you sure to re-create that? This will reset all stored information in the database!'},
        
        'database_not_unique': {'fa':'نام پایگاه داده دستگاه‌ها نبایستی یکسان باشند.',
                'en':'System database names Can not be the same.'},
        
        'restart_change_language': {'fa':'تنظیمات پیکربندی دستگاه ذخیره شدند و نرم‌افزار بایستی جهت اعمال زبان انتخاب شده ریستارت شود.',
                'en':'System configurations are saved successfully and app must be restarted to apply selected language.'},
        
        'modify_user': {'fa':'آیا نسبت به اصلاح این کاربر اطمینان دارید؟',
                'en':'Are you sure to modify this user?'},
        
        'delete_user': {'fa':'آیا نسبت به حذف این کاربر اطمینان دارید؟',
                'en':'Are you sure to delete this user?'},

        'logout_account': {'fa':'آیا نسبت به خروج از حساب کاربری اطمینان دارید؟',
                'en':'Are you sure to logout from account?'},
        
        'username_duplicate': {'fa': 'این نام کاربری قبلا استفاده شده است، لطفا یک نام کاربری دیگر وارد کنید.',
                 'en': 'This username is already taken, Please enter another one.'},
        
        'app_close_confirm': {'fa':'آیا تنظیمات پیکربندی را اعمال و ذخیره نموده و نسبت به خروج از نرم‌افزار اطمینان دارید؟',
                'en':'Are you applied and saved configurations and sure to close the app?'},


}


MESSEGES = {

        'test': {'fa':'تست',
                'en':'This is a test message'},

        'ui_object_created': {'fa':'رابط کاربری نرم‌افزار ایجاد شد.',
                'en':'UI module is created.'},
        
        'api_object_created': {'fa':'ای‌پی‌آی نرم‌افزار ایجاد شد.',
                'en':'API module is created.'},

        'app_closed': {'fa':'نرم‌افزار بسته شد.',
                'en':'App is closed.'},
        
        'app_minimized': {'fa':'نرم‌افزار به نوار وظیفه منتقل شد.',
                'en':'App is minimized to taskbar.'},

        'app_maximized': {'fa':'نرم‌افزار بزرگنمایی شد.',
                'en':'App is maximized.'},
        
        'app_restored_down': {'fa':'نرم‌افزار از حالت بزرگنمایی خارج شد.',
                'en':'App is restored down.'},
        
        'sql_connected': {'fa':'اتصال به اس‌کیوال برقرار شد.',
                'en':'Connection to MySQL Server is established.'},
        
        'database_connected': {'fa':'اتصال به پایگاه داده برقرار شد.',
                'en':'Connection to database is established.'},
        
        'sql_closed': {'fa':'اس‌کیوال بسته شد.',
                'en':'MySQL connection is closed.'},
        
        'db_load_cam_params': {'fa':'پارامترهای دوربین از پایگاه داده دریافت شد.',
                'en':'Cameras parameters is recieved from database.'},

        'build_database_object': {'fa':'ماژول ارتباط با پایگاه داده ساخته شد.',
                'en':'Database module is built.'},
        
        'app_started': {'fa':'نرم‌افزار اجرا شد.',
                'en':'App is started.'},

        'db_update_cam_params': {'fa':'پارامترهای جدید دوربین در پایگاه داده بروزرسانی شدند.',
                'en':'New cameras parameters is updated on database.'},
        
        'get_available_camera_serials': {'fa':'لیست دوربین‌های در دسترس بروزرسانی شد.',
                'en':'Available cameras list is refreshed'},
        
        'db_camera_found_by_serial': {'fa':'یک دوربین با سریال موردنظر پیدا شد.',
                'en':'A camera was found with input camera serial.'},
        
        'camera_connect': {'fa':'اتصال به دوربین با موفقیت برقرار شد.',
                'en':'Connection to the camera is established succussfully.'},

        'reset_data': {'fa':'داده های آماری ریست شد.',
                'en':'The statistical data was reset.'},
                'db_add_user': {'fa':'کاربر جدید در پایگاه داده اضافه شد.',
                'en':'New user is added to database.'},
        
        'db_update_user': {'fa':'اطلاعات جدید کاربر در پایگاه داده بروزرسانی شدند.',
                'en':'User new info are updated on database.'},
        
        'db_delete_user': {'fa':'کاربر از پایگاه داده حذف شد.',
                'en':'User is deleted from database.'},
        
        'user_authenticated': {'fa':'ورود کاربر موفقیت‌آمیز بود.',
                'en':'User login successfull.'},
        
}


TITLES = {

        'test': {'fa':'تست',
                'en':'This is a test title'},
        
        'app_name': {'fa':'نرم‌افزار عرض‌سنج ورق درصا',
                'en':'Dorsa Online Strip Width Gauge'},
        
        'ok': {'fa':'خوب',
                'en':'Ok'},

        'confirm': {'fa':'تایید',
                'en':'Confirm'},

        'cancel': {'fa':'لغو',
                'en':'Cancel'},
        
        'close_app': {'fa':'خروج از نرم‌افزار ',
                'en':'Close App'},
        
        'maximize': {'fa':'بزرگنمایی',
                'en':'Maximize'},

        'restore_down': {'fa':'کوچکنمایی',
                'en':'Restore Down'},
        
        'sql_version': {'fa':'نسخه اس‌کیوال',
                'en':'SQL version'},
        
        'no_serial_assigned': {'fa':'بدون اختصاص',
                'en':'Not assigne'},
        
        'error': {'fa':'خطا',
                'en':'Error'},
        
        'camera_id': {'fa':'شماره دوربین',
                'en':'Camera ID'},

        'camera_serial': {'fa':'سریال دوربین',
                'en':'Camera serial'},
        
        'disconnect': {'fa':'قطع اتصال',
                'en':'Disconnect'},

        'connect': {'fa':'اتصال',
                'en':'Connect'},

        

                
        

        
}
