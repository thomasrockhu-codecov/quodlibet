# Copyright 2004-2005 Joe Wreschnig, Michael Urman
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
# $Id$

import config
import const

from formats._audio import AudioFile

class VCFile(AudioFile):
    def _post_read(self):
        email = config.get("editing", "save_email").strip()
        maps = {"rating": float, "playcount": int}
        for keyed_key, func in maps.items():
            for subkey in ["", ":" + const.EMAIL, ":" + email]:
                key = keyed_key + subkey
                if key in self:
                    try: self["~#" + keyed_key] = func(self[key])
                    except ValueError: pass
                    del(self[key])

        if "totaltracks" in self:
            self.setdefault("tracktotal", self["totaltracks"])
            del(self["totaltracks"])

        # tracktotal is incredibly stupid; use tracknumber=x/y instead.
        if "tracktotal" in self:
            if "tracknumber" in self:
                self["tracknumber"] += "/" + self["tracktotal"]
            del(self["tracktotal"])
        if "disctotal" in self:
            if "discnumber" in self:
                self["discnumber"] += "/" + self["disctotal"]
            del(self["disctotal"])

    def can_change(self, k=None):
        if k is None:
            return super(VCFile, self).can_change(None)
        else: return (super(VCFile, self).can_change(k) and
                      k not in ["totaltracks", "tracktotal", "disctotal",
                                "rating", "playcount"] and
                      not k.startswith("rating:") and
                      not k.startswith("playcount:"))

    def _prep_write(self, comments):
        email = config.get("editing", "save_email").strip()
        for key in comments.keys():
            if key.startswith("rating:") or key.startswith("playcount:"):
                if key.split(":", 1)[1] in [const.EMAIL, email]:
                    del(comments[key])
            else: del(comments[key])

        if config.getboolean("editing", "save_to_songs"):
            email = email or const.EMAIL
            if self["~#rating"] != 0.5:
                comments["rating:" + email] = str(self["~#rating"])
            if self["~#playcount"] != 0:
                comments["playcount:" + email] = str(int(self["~#playcount"]))
