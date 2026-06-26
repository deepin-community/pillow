--- a/setup.py
+++ b/setup.py
@@ -8,6 +8,9 @@
 # ------------------------------
 from __future__ import annotations
 
+from sysconfig import get_platform
+host_platform = get_platform()
+
 import os
 import re
 import shutil
@@ -45,7 +48,7 @@ WEBP_ROOT = None
 ZLIB_ROOT = None
 FUZZING_BUILD = "LIB_FUZZING_ENGINE" in os.environ
 
-if sys.platform == "win32" and sys.version_info >= (3, 14):
+if host_platform == "win32" and sys.version_info >= (3, 14):
     import atexit
 
     atexit.register(
@@ -160,7 +163,7 @@ def _find_library_dirs_ldconfig() -> lis
     args: list[str]
     env: dict[str, str]
     expr: str
-    if sys.platform.startswith("linux") or sys.platform.startswith("gnu"):
+    if host_platform.startswith("linux") or host_platform.startswith("gnu"):
         if struct.calcsize("l") == 4:
             machine = os.uname()[4] + "-32"
         else:
@@ -182,7 +185,7 @@ def _find_library_dirs_ldconfig() -> lis
         env["LC_ALL"] = "C"
         env["LANG"] = "C"
 
-    elif sys.platform.startswith("freebsd"):
+    elif host_platform.startswith("freebsd"):
         args = [ldconfig, "-r"]
         expr = r".* => (.*)"
         env = {}
@@ -556,7 +559,7 @@ class pil_build_ext(build_ext):
         if self.disable_platform_guessing:
             pass
 
-        elif sys.platform == "cygwin":
+        elif host_platform == "cygwin":
             # pythonX.Y.dll.a is in the /usr/lib/pythonX.Y/config directory
             self.compiler.shared_lib_extension = ".dll.a"
             _add_directory(
@@ -566,7 +569,7 @@ class pil_build_ext(build_ext):
                 ),
             )
 
-        elif sys.platform == "darwin":
+        elif host_platform == "darwin":
             # attempt to make sure we pick freetype2 over other versions
             _add_directory(include_dirs, "/sw/include/freetype2")
             _add_directory(include_dirs, "/sw/lib/freetype2/include")
@@ -618,13 +621,13 @@ class pil_build_ext(build_ext):
                 for extension in self.extensions:
                     extension.extra_compile_args = ["-Wno-nullability-completeness"]
         elif (
-            sys.platform.startswith("linux")
-            or sys.platform.startswith("gnu")
-            or sys.platform.startswith("freebsd")
+            host_platform.startswith("linux")
+            or host_platform.startswith("gnu")
+            or host_platform.startswith("freebsd")
         ):
             for dirname in _find_library_dirs_ldconfig():
                 _add_directory(library_dirs, dirname)
-            if sys.platform.startswith("linux") and os.environ.get("ANDROID_ROOT"):
+            if host_platform.startswith("linux") and os.environ.get("ANDROID_ROOT"):
                 # termux support for android.
                 # system libraries (zlib) are installed in /system/lib
                 # headers are at $PREFIX/include
@@ -637,11 +640,11 @@ class pil_build_ext(build_ext):
                     ),
                 )
 
-        elif sys.platform.startswith("netbsd"):
+        elif host_platform.startswith("netbsd"):
             _add_directory(library_dirs, "/usr/pkg/lib")
             _add_directory(include_dirs, "/usr/pkg/include")
 
-        elif sys.platform.startswith("sunos5"):
+        elif host_platform.startswith("sunos5"):
             _add_directory(library_dirs, "/opt/local/lib")
             _add_directory(include_dirs, "/opt/local/include")
 
@@ -657,7 +660,7 @@ class pil_build_ext(build_ext):
             # alpine, at least
             _add_directory(library_dirs, "/lib")
 
-        if sys.platform == "win32":
+        if host_platform == "win32":
             # on Windows, look for the OpenJPEG libraries in the location that
             # the official installer puts them
             program_files = os.environ.get("ProgramFiles", "")
@@ -692,7 +695,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "zlib.h"):
                 if _find_library_file(self, "z"):
                     feature.set("zlib", "z")
-                elif sys.platform == "win32" and _find_library_file(self, "zlib"):
+                elif host_platform == "win32" and _find_library_file(self, "zlib"):
                     feature.set("zlib", "zlib")  # alternative name
                 elif sys.platform == "win32" and _find_library_file(self, "zdll"):
                     feature.set("zlib", "zdll")  # dll import library
@@ -702,7 +705,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "jpeglib.h"):
                 if _find_library_file(self, "jpeg"):
                     feature.set("jpeg", "jpeg")
-                elif sys.platform == "win32" and _find_library_file(self, "libjpeg"):
+                elif host_platform == "win32" and _find_library_file(self, "libjpeg"):
                     feature.set("jpeg", "libjpeg")  # alternative name
 
         feature.set("openjpeg_version", None)
@@ -754,7 +757,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "tiff.h"):
                 if _find_library_file(self, "tiff"):
                     feature.set("tiff", "tiff")
-                if sys.platform in ["win32", "darwin"] and _find_library_file(
+                if host_platform in ["win32", "darwin"] and _find_library_file(
                     self, "libtiff"
                 ):
                     feature.set("tiff", "libtiff")
@@ -860,7 +863,7 @@ class pil_build_ext(build_ext):
         if feature.get("tiff"):
             libs.append(feature.get("tiff"))
             defs.append(("HAVE_LIBTIFF", None))
-            if sys.platform == "win32":
+            if host_platform == "win32":
                 # This define needs to be defined if-and-only-if it was defined
                 # when compiling LibTIFF. LibTIFF doesn't expose it in `tiffconf.h`,
                 # so we have to guess; by default it is defined in all Windows builds.
@@ -872,7 +875,7 @@ class pil_build_ext(build_ext):
         if feature.get("jpeg2000"):
             libs.append(feature.get("jpeg2000"))
             defs.append(("HAVE_OPENJPEG", None))
-            if sys.platform == "win32" and not PLATFORM_MINGW:
+            if host_platform == "win32" and not PLATFORM_MINGW:
                 defs.append(("OPJ_STATIC", None))
         if feature.get("zlib"):
             libs.append(feature.get("zlib"))
@@ -883,7 +886,7 @@ class pil_build_ext(build_ext):
         if feature.get("xcb"):
             libs.append(feature.get("xcb"))
             defs.append(("HAVE_XCB", None))
-        if sys.platform == "win32":
+        if host_platform == "win32":
             libs.extend(["kernel32", "user32", "gdi32"])
         if struct.unpack("h", b"\0\1")[0] == 1:
             defs.append(("WORDS_BIGENDIAN", None))
@@ -920,7 +923,7 @@ class pil_build_ext(build_ext):
 
         if feature.get("lcms"):
             libs = [feature.get("lcms")]
-            if sys.platform == "win32":
+            if host_platform == "win32":
                 libs.extend(["user32", "gdi32"])
             self._update_extension("PIL._imagingcms", libs)
         else:
@@ -933,7 +936,7 @@ class pil_build_ext(build_ext):
         else:
             self._remove_extension("PIL._webp")
 
-        tk_libs = ["psapi"] if sys.platform in ("win32", "cygwin") else []
+        tk_libs = ["psapi"] if host_platform in ("win32", "cygwin") else []
         self._update_extension("PIL._imagingtk", tk_libs)
 
         build_ext.build_extensions(self)
@@ -949,7 +952,7 @@ class pil_build_ext(build_ext):
         print("-" * 68)
         print(f"version      Pillow {PILLOW_VERSION}")
         version = sys.version.split("[")
-        print(f"platform     {sys.platform} {version[0].strip()}")
+        print(f"platform     {host_platform} {version[0].strip()}")
         for v in version[1:]:
             print(f"             [{v.strip()}")
         print("-" * 68)
