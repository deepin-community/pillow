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
@@ -42,7 +45,7 @@ TIFF_ROOT = None
 ZLIB_ROOT = None
 FUZZING_BUILD = "LIB_FUZZING_ENGINE" in os.environ
 
-if sys.platform == "win32" and sys.version_info >= (3, 13):
+if host_platform == "win32" and sys.version_info >= (3, 13):
     import atexit
 
     atexit.register(
@@ -154,7 +157,7 @@ def _find_library_dirs_ldconfig():
     # Based on ctypes.util from Python 2
 
     ldconfig = "ldconfig" if shutil.which("ldconfig") else "/sbin/ldconfig"
-    if sys.platform.startswith("linux") or sys.platform.startswith("gnu"):
+    if host_platform.startswith("linux") or host_platform.startswith("gnu"):
         if struct.calcsize("l") == 4:
             machine = os.uname()[4] + "-32"
         else:
@@ -176,7 +179,7 @@ def _find_library_dirs_ldconfig():
         env["LC_ALL"] = "C"
         env["LANG"] = "C"
 
-    elif sys.platform.startswith("freebsd"):
+    elif host_platform.startswith("freebsd"):
         args = [ldconfig, "-r"]
         expr = r".* => (.*)"
         env = {}
@@ -442,6 +445,38 @@ class pil_build_ext(build_ext):
                 sdk_path = commandlinetools_sdk_path
         return sdk_path
 
+    def add_gcc_paths(self):
+        gcc = sysconfig.get_config_var('CC')
+        tmpfile = os.path.join(self.build_temp, 'gccpaths')
+        if not os.path.exists(self.build_temp):
+            os.makedirs(self.build_temp)
+        ret = os.system('%s -E -v - </dev/null 2>%s 1>/dev/null' % (gcc, tmpfile))
+        is_gcc = False
+        in_incdirs = False
+        inc_dirs = []
+        lib_dirs = []
+        try:
+            if ret >> 8 == 0:
+                with open(tmpfile) as fp:
+                    for line in fp.readlines():
+                        if line.startswith("gcc version"):
+                            is_gcc = True
+                        elif line.startswith("#include <...>"):
+                            in_incdirs = True
+                        elif line.startswith("End of search list"):
+                            in_incdirs = False
+                        elif is_gcc and line.startswith("LIBRARY_PATH"):
+                            for d in line.strip().split("=")[1].split(":"):
+                                d = os.path.normpath(d)
+                                if '/gcc/' not in d:
+                                    _add_directory(self.compiler.library_dirs,
+                                                   d)
+                        elif is_gcc and in_incdirs and '/gcc/' not in line:
+                            _add_directory(self.compiler.include_dirs,
+                                           line.strip())
+        finally:
+            os.unlink(tmpfile)
+
     def build_extensions(self):
         library_dirs = []
         include_dirs = []
@@ -524,7 +559,7 @@ class pil_build_ext(build_ext):
         if self.disable_platform_guessing:
             pass
 
-        elif sys.platform == "cygwin":
+        elif host_platform == "cygwin":
             # pythonX.Y.dll.a is in the /usr/lib/pythonX.Y/config directory
             self.compiler.shared_lib_extension = ".dll.a"
             _add_directory(
@@ -534,7 +569,7 @@ class pil_build_ext(build_ext):
                 ),
             )
 
-        elif sys.platform == "darwin":
+        elif host_platform == "darwin":
             # attempt to make sure we pick freetype2 over other versions
             _add_directory(include_dirs, "/sw/include/freetype2")
             _add_directory(include_dirs, "/sw/lib/freetype2/include")
@@ -585,13 +620,13 @@ class pil_build_ext(build_ext):
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
@@ -604,11 +639,11 @@ class pil_build_ext(build_ext):
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
 
@@ -624,7 +659,7 @@ class pil_build_ext(build_ext):
             # alpine, at least
             _add_directory(library_dirs, "/lib")
 
-        if sys.platform == "win32":
+        if host_platform == "win32":
             # on Windows, look for the OpenJPEG libraries in the location that
             # the official installer puts them
             program_files = os.environ.get("ProgramFiles", "")
@@ -659,7 +694,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "zlib.h"):
                 if _find_library_file(self, "z"):
                     feature.zlib = "z"
-                elif sys.platform == "win32" and _find_library_file(self, "zlib"):
+                elif host_platform == "win32" and _find_library_file(self, "zlib"):
                     feature.zlib = "zlib"  # alternative name
 
         if feature.want("jpeg"):
@@ -667,7 +702,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "jpeglib.h"):
                 if _find_library_file(self, "jpeg"):
                     feature.jpeg = "jpeg"
-                elif sys.platform == "win32" and _find_library_file(self, "libjpeg"):
+                elif host_platform == "win32" and _find_library_file(self, "libjpeg"):
                     feature.jpeg = "libjpeg"  # alternative name
 
         feature.openjpeg_version = None
@@ -719,7 +754,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "tiff.h"):
                 if _find_library_file(self, "tiff"):
                     feature.tiff = "tiff"
-                if sys.platform in ["win32", "darwin"] and _find_library_file(
+                if host_platform in ["win32", "darwin"] and _find_library_file(
                     self, "libtiff"
                 ):
                     feature.tiff = "libtiff"
@@ -834,7 +869,7 @@ class pil_build_ext(build_ext):
         if feature.tiff:
             libs.append(feature.tiff)
             defs.append(("HAVE_LIBTIFF", None))
-            if sys.platform == "win32":
+            if host_platform == "win32":
                 # This define needs to be defined if-and-only-if it was defined
                 # when compiling LibTIFF. LibTIFF doesn't expose it in `tiffconf.h`,
                 # so we have to guess; by default it is defined in all Windows builds.
@@ -846,7 +881,7 @@ class pil_build_ext(build_ext):
         if feature.jpeg2000:
             libs.append(feature.jpeg2000)
             defs.append(("HAVE_OPENJPEG", None))
-            if sys.platform == "win32" and not PLATFORM_MINGW:
+            if host_platform == "win32" and not PLATFORM_MINGW:
                 defs.append(("OPJ_STATIC", None))
         if feature.zlib:
             libs.append(feature.zlib)
@@ -857,7 +892,7 @@ class pil_build_ext(build_ext):
         if feature.xcb:
             libs.append(feature.xcb)
             defs.append(("HAVE_XCB", None))
-        if sys.platform == "win32":
+        if host_platform == "win32":
             libs.extend(["kernel32", "user32", "gdi32"])
         if struct.unpack("h", b"\0\1")[0] == 1:
             defs.append(("WORDS_BIGENDIAN", None))
@@ -894,7 +929,7 @@ class pil_build_ext(build_ext):
 
         if feature.lcms:
             extra = []
-            if sys.platform == "win32":
+            if host_platform == "win32":
                 extra.extend(["user32", "gdi32"])
             self._update_extension("PIL._imagingcms", [feature.lcms] + extra)
         else:
@@ -913,7 +948,7 @@ class pil_build_ext(build_ext):
         else:
             self._remove_extension("PIL._webp")
 
-        tk_libs = ["psapi"] if sys.platform in ("win32", "cygwin") else []
+        tk_libs = ["psapi"] if host_platform in ("win32", "cygwin") else []
         self._update_extension("PIL._imagingtk", tk_libs)
 
         build_ext.build_extensions(self)
@@ -929,7 +964,7 @@ class pil_build_ext(build_ext):
         print("-" * 68)
         print(f"version      Pillow {PILLOW_VERSION}")
         v = sys.version.split("[")
-        print(f"platform     {sys.platform} {v[0].strip()}")
+        print(f"platform     {host_platform} {v[0].strip()}")
         for v in v[1:]:
             print(f"             [{v.strip()}")
         print("-" * 68)
