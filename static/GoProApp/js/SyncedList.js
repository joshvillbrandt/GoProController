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
        this._update();
        var syncer = this;
        this.timer = setInterval(function(){
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
                    var item = data.list[i];
                    updateIDs.push(item['id']);
                    
                    // add or replace html
                    if(item['html'] != undefined) {
                        var row;
                        var el = syncer._listParent.find(syncer._options.itemPrefix+item['id'])
                        if(el.length > 0) row = el.replaceWith(item['html']);
                        else row = syncer._listParent.append(item['html']);
                        
                        // run external update item function
                        if(syncer._options.updateItem != undefined)
                            syncer._options.updateItem(row);
                    }
                }
                
                // auto-delete IDs that we didn't see this time
                for(var i = 0; i < syncer._lastUpdateIDs.length; i++) {
                    if($.inArray(syncer._lastUpdateIDs[i], updateIDs) < 0) {
                        var el = syncer._listParent.find(syncer._options.itemPrefix+syncer._lastUpdateIDs[i])
                        //el.remove();
                        el.fadeOut(2000,function(){$(this).remove();});
                    }
                }
                
                // save current ids for the next update
                syncer._lastUpdateIDs = updateIDs;
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if(syncer._listError != undefined) syncer._listError.show();
                syncer.stopUpdate();
            }
        }); // end ajax
    },
    
    stopUpdate: function() {
        clearInterval(this.timer);
    }
};

function SyncedList(options) {
    this.init(options);
}
