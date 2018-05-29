from streaming.data import socialgist, subscriptions

if __name__ == '__main__':
    sub_manager = subscriptions.SubscriptionManager()
    sg_manager = socialgist.KeywordManager()
    sub_keywords = sub_manager.get_keywords()
    sg_keywords = sg_manager.get_keywords()
    add_list = sub_keywords - sg_keywords
    delete_list = sg_keywords - sub_keywords
    print "Add List:"
    print ",".join(add_list).encode('utf8')
    print "Delete List:"
    print ",".join(delete_list).encode('utf8')
    for key in add_list:
        sg_manager.add_keyword(key)
    for key in delete_list:
        sg_manager.delete_keyword(key)
