odoo.define('inno_web_home.snippet.editor', function (require) {
    'use strict';
    
    var SnippetEditor = require('web_editor.snippet.editor');
    var Class = require('web.Class');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var editor = require('web_editor.editor');
    var animation = require('web_editor.snippets.animation');
    var options = require('web_editor.snippets.options');
    
    var qweb = core.qweb;
    var _t = core._t;
    
    ajax.loadXML('/web_editor/static/src/xml/snippets.xml', qweb);
    console.log(SnippetEditor);
    
    var data = {};
    var NewSnippetEditor = SnippetEditor.Class.include({
        
            create_snippet_editor: function ($snippet) {
                console.log($snippet.context.classList[0]);
                if ($snippet.context.classList[0] == "banner" || $snippet.context.classList[0] == "banner_sub" || $snippet.context.classList[0] == "undefined" || $snippet.context.classList[0] == "disable_customize" || $snippet.context.classList[0] == "slick-list"){
                    return;
                }
                if (typeof $snippet.data("snippet-editor") === 'undefined') {
                    if (!this.activate_overlay_zones($snippet).length) return;
                    $snippet.data("snippet-editor", new SnippetEditor.Editor(this, $snippet));
                }
            }

        
    });
    

    return NewSnippetEditor;
});