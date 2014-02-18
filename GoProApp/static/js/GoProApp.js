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
    // variables
    var updateInterval = 2000;
    var currentRawCam = -1;
    
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
    if($('.camera-list').length > 0) {
        var cameraListURL = '/api/updateCameras/?callback=?';
        if($('.run-raw').length > 0) cameraListURL += '&status';
        cameraList = new SyncedList({
            updateURL: cameraListURL,
            updateInterval: updateInterval,
            listParentSelector: '.camera-list',
            listErrorSelector: '.manager-failed',
            itemPrefix: '#camera-',
            updateItem: function(row, data){
                // bind edit camera
                row.find('a').click(function(e){
                    e.preventDefault();
                    modal.find('.modal-title').html(row.find('.camera-name').html());
                    modal.find('[name=pk]').val(data.id);
                    modal.find('[name=name]').val(row.find('.camera-name').html());
                    modal.find('[name=ssid]').val(row.find('.camera-ssid').html());
                    modal.find('[name=password]').val(row.find('.camera-ssid').attr('title'));
                    modal.find('button').attr('gopro-camera', data.id);
                    modal.find('.existing-camera').show();
                    modal.modal();
                    
                    // image
                    if(data['image'] != undefined)
                        modal.find('.gopro-thumb').attr('src', data['image']);
                    
                    // set this to currentRawCam
                    currentRawCam = data.id;
                    $('.run-raw h3').html('Raw Status Viewer (' + row.find('.camera-name').html() + ')');
                });
                
                // update raw if this is the current raw cam
                if(data['status'] != undefined && data.id == currentRawCam) {
                    var status = $.parseJSON(data['status']);
                    $('.bacpacse').html(status['raw']['bacpac/se']);
                    $('.camerasx').html(status['raw']['camera/sx']);
                    $('.camerase').html(status['raw']['camera/se']);
                    console.debug(status);
                }
            }
        });
    }
    
    // initialize command list manager
    if($('.command-list').length > 0) {
        commandList = new SyncedList({
            updateURL: '/api/updateCommands/?callback=?',
            updateInterval: updateInterval,
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
    }
    
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
        modal.modal('hide');
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
    
    // raw output visualizer
    if($('.run-raw').length > 0) {
        $('.raw-hold-button').click(function(e){
            e.preventDefault();
            $('.raw-group').each(function(){
                var group = $(this);
                var status = group.find('div:not(.raw-hold)').html();
                group.find('.raw-hold').attr('status-hold', status);
            });
        });
        setInterval(function(){
            $('.raw-group').each(function(){
                var group = $(this);
                var status = group.find('div:not(.raw-hold)').html();
                var holdStatus = group.find('.raw-hold').attr('status-hold');
                var diff = '';
                
                if(holdStatus != undefined) {
                    for(var i = 0; i < status.length; i++) {
                        if(status[i] == holdStatus[i]) diff += holdStatus[i];
                        else diff += "<span>" + holdStatus[i] + "</span>";
                    }
                    group.find('.raw-hold').html(diff);
                }
            });
        }, updateInterval);
    }
    
    // initialize preview list manager
    if($('.preview-list').length > 0) {
        var cameraListURL = '/api/updateCameras/?callback=?&preview';
        cameraList = new SyncedList({
            updateURL: cameraListURL,
            updateInterval: updateInterval,
            listParentSelector: '.preview-list',
            listErrorSelector: '.manager-failed',
            itemPrefix: '#camera-',
            updateItem: function(row, data){
                // image
                if(data['image'] != undefined)
                    row.find('.gopro-thumb').attr('src', data['image']);
            }
        });
    }
    
}); // end document ready