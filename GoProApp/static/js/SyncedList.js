 /**
 * SyncedList.js
 * Description: Continuous synchronization of a list between a server and a client.
 * Requires: jQuery >= 1.10
 * Author: Josh Villbrandt
 * Date: August 2013
 */

SyncedList.prototype = {
    defaultOptions: {
        updateURL: '/api/',
        updateInterval: 10000, // milliseconds
        listParentSelector: '',
        listErrorSelector: '',
        itemPrefix: '.itemid-',
        updateItem: undefined,
    },
    _lastUpdateTime: undefined, // set by server
    _lastUpdateIDs: [],
    _listParent: undefined,
    _listError: undefined,
    _timer: undefined,

    init: function(options) {
        // build options
        this._options = {};
        $.extend(true, this._options, this.defaultOptions, options);
        
        // find dom elements
        if(this._options['listParentSelector'] != undefined)
            this._listParent = $(this._options['listParentSelector']);
        if(this._options['listErrorSelector'] != undefined)
            this._listError = $(this._options['listErrorSelector']);
        
        // start updater
        this.restartTimer();
    },
    
    restartTimer: function() {
        // stop the timer if it is currently running
        if(this._timer != undefined) clearInterval(this._timer);
        
        // immediately run the update function
        this._update();
        
        // restart the timer
        var syncer = this;
        this._timer = setInterval(function(){
            syncer._update();
        }, this._options.updateInterval);
    },
    
    _update: function() {
        // update list
        var syncer = this;
        $.ajax({
            dataType: "json",
            url: this._options.updateURL,
            data: {last_update: this._lastUpdateTime},
            success: function(data, textStatus, jqXHR) {
                syncer._lastUpdateTime = data.time;
                
                // update list
                var updateIDs = [];
                for(var i = 0; i < data.list.length; i++) {
                    // setup
                    var item = data.list[i];
                    updateIDs.push(item['id']);
                    var el = syncer._listParent.find(syncer._options.itemPrefix+item['id']);
                    
                    // add or replace html
                    if(item['html'] != undefined) {
                        if(el.length > 0) el.replaceWith(item['html']);
                        else syncer._listParent.append(item['html']);
                        
                        // run external update item function
                        if(syncer._options.updateItem != undefined) {
                            el = syncer._listParent.find(syncer._options.itemPrefix+item['id']);
                            syncer._options.updateItem(el, item);
                        }
                    }
                    
                    // process in extra item params
                    if(item['extra'] != undefined) {
                        for(var selector in item['extra']) {
                            el.find(selector).html(item['extra'][selector]);
                        }
                    }
                }
                
                // auto-delete IDs that we didn't see this time
                for(var i = 0; i < syncer._lastUpdateIDs.length; i++) {
                    if($.inArray(syncer._lastUpdateIDs[i], updateIDs) < 0) {
                        var el = syncer._listParent.find(syncer._options.itemPrefix+syncer._lastUpdateIDs[i])
                        el.remove();
                        //el.fadeOut(2000,function(){$(this).remove();});
                    }
                }
                
                // save current ids for the next update
                syncer._lastUpdateIDs = updateIDs;
                
                // process in extra list params
                if(data.extra != undefined) {
                    for(var key in data.extra) {
                        $(key).html(data.extra[key]);
                    }
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if(syncer._listError != undefined) syncer._listError.show();
                syncer.stopUpdate();
            }
        }); // end ajax
    },
    
    stopUpdate: function() {
        if(this._timer != undefined) clearInterval(this._timer);
    }
};

function SyncedList(options) {
    this.init(options);
}
