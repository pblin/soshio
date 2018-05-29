#!/usr/bin/python
# -*- coding: utf-8 -*-

import mongo

def get(polarity=False, display=False, synonyms=False):
    with mongo.get_collection('sentiments') as collection:
        for label in collection.find():
            result = [label['_id']]
            if polarity: result.append(label['polarity'])
            if display: result.append(label['display'])
            if synonyms: result.append(label['synonyms'])
            yield tuple(result)
            
def init():
    with mongo.get_collection('sentiments') as collection:
        for doc in map(to_dict, models):
            collection.save(doc)

models = [
        ('love', 0.9999,
            {'en':'Love', 'zh-tw':u'愛', 'zh-cn':u'爱'}, 
             [u'亲', u'佳', u'喜', u'嗜', u'帅', u'棒', u'炫', u'爱', u'美', u'赞', u'酷', u'不错', u'中意', u'亲爱', u'伟大', u'光荣', u'光辉', u'可亲', u'可爱', u'喜欢', u'大赞', u'大赞', u'太棒', u'好棒', u'帅气', u'很好', u'很爱', u'怜爱', u'感动', u'感谢', u'抢购', u'拥趸', u'挚爱', u'最好', u'最爱', u'最美', u'欣赏', u'死忠', u'清新', u'满意', u'火热', u'爱惜', u'牛逼', u'犀利', u'珍惜', u'甜美', u'甜蜜', u'祈福', u'称赞', u'给力', u'美味', u'美好', u'美梦', u'良药', u'荣光', u'荣耀', u'衷心', u'诱人', u'赛高', u'轻巧', u'酷炫', u'风靡', u'香甜', u'么么哒', u'不哭站撸', u'如胶似漆', u'心甘情愿']),
        ('joy', 0.7999, 
            {'en':'Joy', 'zh-tw':u'喜', 'zh-cn':u'喜'}, 
            [u'乐', u'哏', u'噗', u'福', u'笑', u'趣', u'逗', u'中奖', u'乐子', u'偷笑', u'喜悦', u'嘻嘻', u'嘿嘿', u'大笑', u'好玩', u'好运', u'如意', u'妥妥', u'开心', u'快乐', u'惊喜', u'愉快', u'有趣', u'欢乐', u'欢喜', u'欢欣', u'欢腾', u'温馨', u'满意', u'满足', u'爆笑', u'痛快', u'知足', u'祥和', u'福气', u'笑果', u'精彩', u'趣味', u'逗比', u'高兴', u'不差钱', u'有意思', u'哈哈大笑', u'喜大普奔', u'大快人心', u'姹紫嫣红', u'春风得意', u'普天同庆', u'欢欣鼓舞', u'赏心乐事']),
        ('anger', -0.9999, 
            {'en':'Anger', 'zh-tw':u'怒', 'zh-cn':u'怒'},
            [u'呸', u'哼', u'怒', u'愤', u'烦', u'你妹', u'冷眼', u'凶恶', u'出离', u'去死', u'喷子', u'坑人', u'害人', u'怨恨', u'打飞', u'抓狂', u'无理', u'无语', u'暴力', u'暴徒', u'棒槌', u'死开', u'滚开', u'生气', u'缺德', u'腐败', u'蛮横', u'蠢货', u'该死', u'躺枪', u'迂腐', u'过分', u'鸟事', u'鸟人', u'TMD', u'不是人', u'不要脸', u'官二代', u'有病啊', u'没人性', u'没天理', u'不给面子', u'义愤填膺', u'天怒人怨', u'社病我药', u'穷凶极恶']),
        ('fear', -0.7999, 
            {'en':'Fear', 'zh-tw':u'懼', 'zh-cn':u'惧'},
            [u'忧', u'怕', u'怖', u'怯', u'恐', u'惧', u'惧', u'惨', u'惶', u'不敢', u'倒霉', u'发抖', u'害怕', u'心惊', u'恐怖', u'惊悚', u'惊慌', u'惶惶', u'战栗', u'畏惧', u'皱眉', u'躲远', u'逃跑', u'霉头', u'霉运', u'颤抖', u'颤栗', u'坏运气', u'不能面对', u'大惊失色', u'头皮发麻', u'心惊胆战', u'担惊受怕', u'提心吊胆', u'望风而逃', u'目瞪口呆', u'细思恐极', u'退避三舍', u'面无血色', u'骇人听闻']),
        ('loathe', -0.9999, 
            {'en':'Loathe', 'zh-tw':u'惡', 'zh-cn':u'恶'},
            [u'丑', u'俗', u'假', u'厌', u'坏', u'差', u'烂', u'疯', u'贱', u'贱', u'万恶', u'不好', u'丑哭', u'丢脸', u'伪劣', u'低俗', u'假冒', u'傻b', u'傻逼', u'冒牌', u'卧槽', u'厌恶', u'厌烦', u'去死', u'反感', u'古板', u'可恶', u'吐槽', u'呆板', u'坏了', u'坑人', u'坑爹', u'太瞎', u'恶劣', u'恶意', u'抓狂', u'无耻', u'残次', u'渣子', u'渣渣', u'脑残', u'艳俗', u'讨厌', u'过时', u'过气', u'TMD', u'不喜欢', u'人干事', u'何弃疗', u'坑惨了', u'惹不起', u'我伙呆', u'战五渣', u'杀马特', u'样子货', u'猪一样', u'神经病', u'肥猪流', u'人人喊打', u'十动然拒', u'顶你个肺']),
        ('sorrow', -0.7999, 
            {'en':'Sorrow', 'zh-tw':u'哀', 'zh-cn':u'哀'},
            [u'哀', u'唉', u'悲', u'愁', u'泪', u'疼', u'苦', u'败', u'不好', u'伤心', u'失败', u'孤独', u'心寒', u'悲痛', u'无奈', u'无语', u'沮丧', u'泪奔', u'穷屌', u'等死', u'脑残', u'苦逼', u'苦闷', u'血泪', u'覆辙', u'重蹈', u'难过', u'默默', u'散了吧', u'洗洗睡', u'给跪了', u'脑残粉', u'请允悲', u'人艰不拆', u'内牛满面', u'地命海心', u'失声痛哭', u'泪流满面', u'男默女泪', u'累觉不爱', u'重蹈覆辙']),
        ('desire', 0.5999, 
            {'en':'Desire', 'zh-tw':u'慾', 'zh-cn':u'欲'},
            [u'求', u'力推', u'力荐', u'大爱', u'嫉妒', u'对味', u'希望', u'幻想', u'心水', u'想要', u'憧憬', u'推荐', u'改变', u'期待', u'求粉', u'渴望', u'祈祷', u'羡慕', u'豪华', u'跪求', u'转变', u'转运', u'逆袭', u'长草', u'天了噜', u'涨姿势', u'碉堡了', u'等不急', u'不明觉厉', u'美梦成真', u'长命百岁', u'羡慕嫉妒恨']),
    ]
    
to_dict = lambda item: {'_id':item[0], 'polarity':item[1], 'display':item[2], 'synonyms':item[3]}

if __name__ == '__main__':
    init()
