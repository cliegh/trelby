# -*- coding: utf-8 -*-
import config
import mypickle
import screenplay
import util

# manages auto completion information for a single script.
# 단일 스크립트의 자동완성 기능관리
class AutoCompletion:
    def __init__(self):
        # type configs, key = line type, value = Type
        # diction형태로 type이 들어가는데 key는 line type과 value는 Type이 들어감
        self.types = {}

        # element types
        # 요소 유형
        t = Type(screenplay.SCENE)  #씬 정보
        self.types[t.ti.lt] = t

        t = Type(screenplay.CHARACTER)  #캐릭터
        self.types[t.ti.lt] = t

        t = Type(screenplay.TRANSITION) #Transition
        t.items = [
            "BACK TO:",
            "CROSSFADE:",
            "CUT TO:",
            "DISSOLVE TO:",
            "FADE IN:",
            "FADE OUT",
            "FADE TO BLACK",
            "FLASHBACK TO:",
            "JUMP CUT TO:",
            "MATCH CUT TO:",
            "SLOW FADE TO BLACK",
            "SMASH CUT TO:",
            "TIME CUT:"
            ]
        self.types[t.ti.lt] = t
        
        t = Type(screenplay.SHOT)   #샷에대한 정보 들어감
        self.types[t.ti.lt] = t

        self.refresh()

    # load config from string 's'. does not throw any exceptions, silently
    # ignores any errors, and always leaves config in an ok state.
    def load(self, s):
        vals = mypickle.Vars.makeVals(s)

        for t in self.types.itervalues():
            t.load(vals, "AutoCompletion/")

        self.refresh()

    # save config into a string and return that.
    def save(self):
        s = ""

        for t in self.types.itervalues():
            s += t.save("AutoCompletion/")

        return s

    # fix up invalid values and uppercase everything.
    def refresh(self):
        for t in self.types.itervalues():
            tmp = []

            for v in t.items:
                v = util.upper(util.toInputStr(v)).strip()

                if len(v) > 0:
                    tmp.append(v)

            t.items = tmp

    # get type's Type, or None if it doesn't exist.
    def getType(self, lt):
        return self.types.get(lt)

# auto completion info for one element type
# 한개의 요소가 들어가는 자동완성 기능.
class Type:
    cvars = None

    def __init__(self, lt):

        # pointer to TypeInfo
        self.ti = config.lt2ti(lt)

        if not self.__class__.cvars:
            v = self.__class__.cvars = mypickle.Vars()

            v.addBool("enabled", True, "Enabled")
            v.addList("items", [], "Items",
                      mypickle.StrLatin1Var("", "", ""))

            v.makeDicts()

        self.__class__.cvars.setDefaults(self)

    def save(self, prefix):
        prefix += "%s/" % self.ti.name

        return self.cvars.save(prefix, self)

    def load(self, vals, prefix):
        prefix += "%s/" % self.ti.name

        self.cvars.load(vals, prefix, self)
