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
    // grab modal
    var modal = $('#camera-modal');
    
    // bind to add camera
    $('.gopro-addcamera').click(function(e){
        e.preventDefault();
        modal.find('.modal-title').html('Add Camera');
        modal.find('[name=pk]').val('new');
        modal.find('[name=name]').val('');
        modal.find('[name=ssid]').val('');
        modal.find('[name=password]').val('');
        modal.find('.gopro-deletecamera').attr('gopro-camera', '');
        modal.find('.existing-camera').hide();
        modal.modal();
    });
    
    // Save Camera Form
    modal.find('form').submit(function(e){
        e.preventDefault();
        
        var args = {
            pk: modal.find('[name=pk]').val(),
            name: modal.find('[name=name]').val(),
            ssid: modal.find('[name=ssid]').val(),
            password: modal.find('[name=password]').val(),
        };
        $.getJSON('/api/editCamera/?callback=?', args, function(data, textStatus, jqXHR) {
            cameraList.restartTimer();
        });
        modal.modal('hide');
    });
    
    // initialize camera list manager
    cameraList = new SyncedList({
        updateURL: '/api/updateCameras/?callback=?',
        updateInterval: 2000,
        listParentSelector: '.camera-list',
        listErrorSelector: '.manager-failed',
        itemPrefix: '#camera-',
        updateItem: function(row){
            // bind edit camera
            row.find('a').click(function(e){
                e.preventDefault();
                var cameraID = row.attr('gopro-camera');
                modal.find('.modal-title').html(row.find('.camera-name').html());
                modal.find('[name=pk]').val(cameraID);
                modal.find('[name=name]').val(row.find('.camera-name').html());
                modal.find('[name=ssid]').val(row.find('.camera-ssid').html());
                modal.find('[name=password]').val(row.find('.camera-ssid').attr('title'));
                modal.find('button').attr('gopro-camera', cameraID);
                modal.find('.existing-camera').show();
                modal.modal();
            });
        }
    });
    
    // initialize command list manager
    commandList = new SyncedList({
        updateURL: '/api/updateCommands/?callback=?',
        updateInterval: 2000,
        listParentSelector: '.command-list',
        listErrorSelector: '.manager-failed',
        itemPrefix: '#command-',
        updateItem: function(row){
            // bind delete command
            row.find('a.gopro-deletecommand').click(function(e){
                e.preventDefault();
                var commandID = $(this).attr('gopro-command');
                
                // push to server
                var args = {pk: commandID};
                $.getJSON('/api/deleteCommand/?callback=?', args, function(data, textStatus, jqXHR) {
                    // the syncer will automatically delete this row if the app really gets rid of it
                    commandList.restartTimer();
                });
            });
        }
    });
    
    // bind send command
    $('.gopro-sendcommand').click(function(e){
        e.preventDefault();
        var el = $(this);
        var cameraID = el.attr('gopro-camera'), command = el.attr('gopro-command');
        
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
        $.getJSON('/api/sendCommands/?callback=?', args, function(data, textStatus, jqXHR) {
            commandList.restartTimer();
        });
    });
    
    // bind delete camera
    $('.gopro-deletecamera').click(function(e){
        e.preventDefault();
        var el = $(this);
        
        // push to server
        var args = {pk: el.attr('gopro-camera')};
        $.getJSON('/api/deleteCamera/?callback=?', args, function(data, textStatus, jqXHR) {
            cameraList.restartTimer();
        });
        modal.modal('hide');
    });
    
}); // end document ready