 /**
 * GoProApp - GoProApp.js
 * Description: Primary JS script for the GoProApp.
 * Requires: jQuery >= 1.10, SyncedList.js
 * Author: Josh Villbrandt
 * Date: August 2013
 */

// scoping variables here so that it is easy to debug via the console
var cameraList, commandList;

$(document).ready(function(){
    // initialize camera list manager
    cameraList = new SyncedList({
        updateURL: '/api/updateCameras/?callback=?',
        updateInterval: 2000,
        listParentSelector: '.camera-list',
        listErrorSelector: '.manager-failed',
        itemPrefix: '#camera-',
    });
    
    // initialize command list manager
    commandList = new SyncedList({
        updateURL: '/api/updateCommands/?callback=?',
        updateInterval: 2000,
        listParentSelector: '.command-list',
        listErrorSelector: '.manager-failed',
        itemPrefix: '#command-',
        updateItem: function(row){
            // delete command
            row.find('a.gopro-deletecommand').click(function(e){
                e.preventDefault();
                var commandID = $(this).attr('gopro-command');
                
                // push to server
                var args = {command: commandID};
                $.getJSON('/api/deleteCommand/?callback=?', args, function(data, textStatus, jqXHR) {
                    // the syncer will automatically delete this row if the app really gets rid of it
                });
            });
        }
    });
    
    // send command
    $('a.gopro-sendcommand').click(function(e){
        e.preventDefault();
        var a = $(this);
        var cameraID = a.attr('gopro-camera'), command = a.attr('gopro-command');
        
        var commands = [];
        var cameras = cameraList._lastUpdateIDs;
        if(cameraID == 'all') {
            for(var i = 0; i < cameras.length; i++) {
                commands.push([cameras[i], command]);
            }
        }
        else commands.push([cameraID, command]);
        
        // push to server
        var args = {commands: JSON.stringify(commands)};
        console.log(args)
        $.getJSON('/api/sendCommands/?callback=?', args, function(data, textStatus, jqXHR) {
        });
    });
    
}); // end document ready