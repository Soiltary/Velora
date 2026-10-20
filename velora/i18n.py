"""English and Arabic UI strings with isolated Latin tokens in Arabic sentences."""
from __future__ import annotations
import re
_language = 'en'
_reverse = {}
STRINGS = {
'Updates':'التحديثات',
'Check updates':'فحص التحديثات',
'Checking updates...':'جارٍ فحص التحديثات',
'Downloading update...':'جارٍ تنزيل التحديث',
'Update available':'يتوفر تحديث',
'An update is available. Use Check updates to install it.':'يتوفر تحديث جديد، اضغط فحص التحديثات لتثبيته',
'You have the latest version.':'لديك أحدث إصدار',
'Finish the current conversion before updating.':'أكمل التحويل الجاري قبل تثبيت التحديث',
'Wait for the update operation to finish.':'انتظر انتهاء عملية التحديث',
'Install update now? Velora will close and reopen. Settings and personal files are kept.':'هل تريد تثبيت التحديث الآن؟ سيُغلق Velora ويُفتح مجددًا مع الاحتفاظ بإعداداتك وملفاتك',
'Could not download or verify the update. Your installed version is unchanged.':'تعذّر تنزيل التحديث أو التحقق منه، النسخة الحالية محفوظة',
'Could not launch the updater. Please try again.':'تعذّر تشغيل التحديث، حاول مجددًا',
'A new form. The same flow.':'ملفاتك بشكل جديد',
'Drop files. Change their form.':'ملفاتك بشكل جديد',
'Images · Video · Audio · PDF · Documents · Spreadsheets · Subtitles':'صور • فيديو • صوت • PDF • مستندات • جداول • ترجمة',
'●  LOCAL PROCESSING':'●  المعالجة على جهازك',
'Shortcuts':'الاختصارات', 'Help':'المساعدة', 'Support':'دعم',
'+ Add files':'+ إضافة ملفات', '+ Folder':'+ مجلد', 'Clear':'مسح', 'Open wheel':'فتح الدائرة',
'FILE':'الملف', 'SIZE':'الحجم', 'STATUS':'الحالة', 'Convert':'تحويل', 'Tools':'الأدوات',
'Merge PDFs':'دمج ملفات PDF', 'Convert files':'بدء التحويل', 'Apply tool':'تطبيق الأداة',
'Cancel':'إلغاء', 'Save':'حفظ', 'OK':'موافق', 'Close':'إغلاق', 'Choose folder':'اختيار مجلد',
'Reset':'إعادة تعيين', 'Show output':'فتح مجلد النتائج', 'Enable drag wheel':'تفعيل دائرة السحب',
'Ready. Original files are always preserved.':'جاهز • تُحفظ ملفاتك الأصلية دائمًا',
'Ready':'جاهز', 'Queued':'في الانتظار', 'Folder':'مجلد', 'Missing':'غير موجود', 'Cancelled':'أُلغي',
'Failed — double-click for details':'تعذّر التحويل • انقر مرتين للتفاصيل',
'Processing locally…':'جارٍ التحويل على جهازك…',
'Cancelling… completed files are preserved.':'جارٍ الإلغاء… تُحفظ الملفات المكتملة',
'Output: Velora Output beside each original':'الحفظ: مجلد Velora Output بجانب كل ملف أصلي',
'Open Velora':'فتح Velora', 'Quit':'خروج', 'Velora — Drag a file, tap Shift':'Velora — اسحب ملفًا واضغط Shift',
'Remove metadata':'حذف البيانات الوصفية', 'Split PDF':'تقسيم PDF', 'Extract audio':'استخراج الصوت',
'Resize':'تغيير الحجم', 'Rotate 90°':'تدوير 90°', 'Grayscale':'تدرج رمادي', 'Compress':'ضغط', 'Trim':'قص',
'Copy path':'نسخ المسار', 'Show folder':'فتح المجلد', 'Drop on a format':'أفلت على الصيغة', 'Drag files here':'اسحب الملفات هنا',
'Actions':'إجراءات', 'Word (.docx)':'Word (.docx)',
'Choose files':'اختيار الملفات', 'Choose folder to ZIP':'اختيار مجلد لضغطه بصيغة ZIP', 'Output folder':'مجلد حفظ النتائج',
'Conversion details':'تفاصيل التحويل', 'Keyboard shortcuts':'اختصارات لوحة المفاتيح',
'Open the wheel before dragging a file.':'افتح الدائرة أولًا ثم اسحب الملف إليها',
'Open / hide wheel':'فتح الدائرة أو إخفاؤها',
'Examples: Ctrl+Space, Alt+Q, Ctrl+F8\nA combination already used by another app cannot be saved.':'أمثلة: Ctrl+Space أو Alt+Q أو Ctrl+F8\nلا يمكن حفظ اختصار مستخدم في تطبيق آخر',
'Ctrl+Shift+Space opens Velora. Escape closes the wheel.\nShift / Alt / Ctrl during dragging keep their existing actions.':'يفتح Ctrl+Shift+Space البرنامج ويغلق Escape الدائرة\nتحتفظ مفاتيح Shift وAlt وCtrl بوظائفها أثناء السحب',
'Wait for the current batch to finish before adding files.':'انتظر اكتمال المجموعة الحالية قبل إضافة ملفات',
'Wait for the current conversion to finish.':'انتظر اكتمال عملية التحويل الحالية',
'Current batch is still running. Drop these files again when it finishes.':'المجموعة الحالية قيد المعالجة • أعد إسقاط الملفات بعد اكتمالها',
'Shortcut unavailable':'الاختصار غير متاح',
'Shortcut unavailable — open Shortcuts to choose another.':'الاختصار غير متاح • اختر غيره من إعدادات الاختصارات',
'Desktop-wide key polling is available on Windows.':'الاختصارات العامة متاحة على ويندوز',
'Width':'العرض', 'Height':'الارتفاع', 'Quality':'الجودة', 'Start (seconds)':'البداية (بالثواني)', 'End (seconds)':'النهاية (بالثواني)',
'Fits within these bounds. Aspect ratio is preserved.':'تُحفظ نسبة الأبعاد دون تجاوز الحدود المختارة',
'Quality applies to JPEG images. PDF uses lossless\ncleanup; video uses H.264 at CRF 28. Size may vary.':'الجودة لصور JPEG • تنظيف PDF دون فقدان\nيُضغط الفيديو بترميز H.264 وقيمة CRF 28 • قد يختلف الحجم',
'Support Velora':'ادعم استمرار Velora',
'If you would like to support the creator and help keep Velora growing, use the button below.':'إذا تبغى تدعم صاحب الأداة عشان يستمر في تطوير Velora اضغط على الزر أدناه',
'Support is optional and appreciated.':'دعمك اختياري ومحل تقدير',
'Support Velora ↗':'ادعم استمرار Velora ↗',
'Velora help':'مساعدة Velora',
'DOCX to PDF works locally without Office using a basic layout. Install LibreOffice for richer formatting.':'تحويل DOCX إلى PDF يعمل محليًا بتنسيق مبسط وصفحات مصوّرة • ثبّت LibreOffice للحفاظ على تنسيق أغنى ونص قابل للتحديد',
'PDF to Word keeps editable text; scanned pages remain images. No OCR.':'تحويل PDF إلى Word يحفظ النص القابل للتعديل والصفحات الممسوحة كصور • لا يشمل التعرّف الضوئي على النصوص',
'Choose PDF or DOCX files, then select the output format.':'أضف ملفات PDF أو DOCX ثم اختر صيغة الناتج',
'PDF → Word · Word → PDF':'تحويل PDF إلى Word والعكس',
'Basic Word export: text, tables and inline images. Headers, footers, floating shapes and complex layouts may change.':'تصدير Word المبسط يدعم النصوص والجداول والصور المضمّنة • قد تتغير الترويسات والتذييلات والأشكال العائمة والتنسيقات المعقدة',
'PDF pages: export JPG/PNG, split, merge or extract text.':'صفحات PDF: تصدير JPG وPNG وتقسيم ودمج واستخراج النصوص',
'Your files stay on this device. Original files are preserved.':'تبقى الملفات على جهازك وتُحفظ النسخ الأصلية',
'Global shortcut:':'الاختصار العام:',
'Press the shortcut, then drag onto the wheel. Closing the window keeps Velora in the system tray. Use Quit to stop it.':'اضغط الاختصار ثم اسحب الملف إلى الدائرة • إغلاق النافذة يبقي Velora بجانب الساعة • اختر خروج لإيقافه',
'Password-protected PDFs must be unlocked before conversion.':'أزل كلمة المرور عن ملف PDF قبل تحويله',
'Word export supports up to 250 PDF pages per file.':'تصدير Word يدعم حتى 250 صفحة PDF لكل ملف',
'Word to PDF supports up to 250 output pages.':'تحويل Word إلى PDF يدعم حتى 250 صفحة ناتجة',
'This Word document is too large to unpack.':'مستند Word أكبر من حد فك الضغط',
'A Word image could not be decoded. Use PNG or JPG images.':'تعذر فتح إحدى صور Word • استخدم صور PNG أو JPG',
'This conversion needs LibreOffice. Install it from libreoffice.org, then retry.':'هذا التحويل يتطلب LibreOffice • ثبّته من libreoffice.org ثم أعد المحاولة',
'Unlock protected PDFs before merging.':'أزل الحماية عن ملفات PDF قبل الدمج',
'No output data. Scanned PDFs need OCR, which this version does not include.':'لا توجد بيانات ناتجة • استخراج نص الصفحات الممسوحة يتطلب OCR وهو غير مضمّن',
'No valid subtitle cues found. Use a UTF-8 SRT or VTT file.':'لا توجد مقاطع ترجمة صالحة • استخدم ملف SRT أو VTT بترميز UTF-8',
'Choose an output folder outside the folder being archived.':'اختر مجلد حفظ خارج المجلد الذي يتم ضغطه',
'Conversion timed out':'انتهت مهلة التحويل', 'Converter failed':'تعذّر التحويل',
'No changes were made to your original files.':'لم تتغير ملفاتك الأصلية',
}

STRINGS.update({
'Choose one key combination, such as Ctrl+Space or Alt+Q.':'اختر اختصارًا واحدًا مثل Ctrl+Space أو Alt+Q',
'Include Ctrl or Alt so normal typing is not intercepted.':'استخدم Ctrl أو Alt لتجنب التأثير على الكتابة العادية',
'Use Ctrl or Alt instead of the Windows key.':'استخدم Ctrl أو Alt بدل مفتاح ويندوز',
'Use Space, a letter, a number, or F1–F12 with Ctrl or Alt.':'استخدم Space أو حرفًا أو رقمًا أو F1–F12 مع Ctrl أو Alt',
'Ctrl+Shift+Space is reserved for the main window.':'اختصار Ctrl+Shift+Space مخصص لفتح النافذة الرئيسية',
'Global shortcuts require Windows.':'الاختصارات العامة تتطلب ويندوز',
'LibreOffice did not produce an output. The input may be unsupported or protected.':'لم ينتج LibreOffice ملفًا • قد يكون الإدخال غير مدعوم أو محميًا',
'End must be greater than start; times are seconds.':'وقت النهاية يجب أن يكون بعد البداية • الوقت بالثواني',
'Too many output files with the same name':'عدد الملفات الناتجة بالاسم نفسه كبير جدًا',
'Choose at least two PDF files. Queue order is merge order.':'اختر ملفي PDF على الأقل • تُدمج بالترتيب الظاهر في القائمة',
})


def language():
    return _language


def set_language(value):
    global _language
    _language = 'ar' if value == 'ar' else 'en'


def source(value):
    return _reverse.get(value, value)


def tr(value):
    if not isinstance(value, str):
        return value
    value = source(value)
    if _language != 'ar':
        return value
    translated = STRINGS.get(value)
    if translated is None:
        patterns = [
            (r'^(.*) is already in use or reserved by Windows. Choose another shortcut.$', lambda m:f'الاختصار {m[1]} مستخدم أو محجوز بواسطة ويندوز • اختر اختصارًا آخر'),
            (r'^(\d+) file\(s\) in queue\. Double-click a row to reveal its output or error\.$', lambda m:f'{m[1]} ملفات في قائمة الانتظار • انقر مرتين لعرض النتيجة أو الخطأ'),
            (r'^Done · (\d+) output\(s\)$', lambda m:f'اكتمل • {m[1]} ملفات ناتجة'),
            (r'^Finished: (\d+) succeeded, (\d+) failed or cancelled\.$', lambda m:f'اكتمل: {m[1]} نجح • {m[2]} تعذّر أو أُلغي'),
            (r'^Output: (.*)$', lambda m:'الحفظ: ' + ('مجلد Velora Output بجانب كل ملف أصلي' if m[1]=='Velora Output beside each original' else m[1])),
            (r'^Wheel shortcut: (.*) — works in the background\.$', lambda m:f'اختصار الدائرة: {m[1]} • يعمل في الخلفية'),
            (r'^(.*) settings$', lambda m:tr(m[1])+' — الإعدادات'),
        ]
        translated = value
        for pattern, render in patterns:
            match = re.fullmatch(pattern, value, re.S)
            if match:
                translated = render(match)
                break
    if re.search(r'[\u0590-\u08ff]', translated):
        translated = re.sub(r'[A-Za-z0-9][A-Za-z0-9._/+:\\-]*(?: +[A-Za-z0-9][A-Za-z0-9._/+:\\-]*)*', lambda m:'\u2066'+m[0]+'\u2069', translated)
    _reverse[translated] = value
    return translated
