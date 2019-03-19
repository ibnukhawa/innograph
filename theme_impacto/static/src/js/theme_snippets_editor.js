odoo.define('theme_impacto.theme.snippets.editor', function (require) {
    'use strict';

    var widget = require('web_editor.widget');
    var animation = require('web_editor.snippets.animation');
    var options = require('web_editor.snippets.options');
    var snippet_editor = require('web_editor.snippet.editor');
    var editor = require('web_editor.editor');
    var MediaDialog = require('web_editor.widget').MediaDialog;
    var ajax = require('web.ajax');
    var core = require('web.core');
     var Model = require('web.Model');
    var qweb = core.qweb;
    var _t = core._t;
   


    ajax.loadXML('/theme_impacto/static/src/xml/html_block.xml', qweb);
    /*ajax.loadXML('/theme_impacto/static/src/xml/update_skill.xml', qweb);*/

      options.registry.tabslide = options.Class.extend({
      start : function () {
          var self = this;
          this._super();
          this.id = this.$target.attr("id");
          this.$inner = this.$target.find("div[class='tab-content']");
          this.$indicators = this.$target.find("ul[role='tablist']");
      },    
      add_tab: function(type,value) {
          var self = this;
          if(type !== "click") return;
      if (type == "click" || type==undefined){
        var self = this;
          var cycle = this.$inner.length;
          var id=new Date().getTime();
          this.$indicators.append('<li role="presentation"><a href="#'+id+'" aria-controls="profile" role="tab" data-toggle="tab">New Tab</a></li>');
        this.$inner.append('<div role="tabpanel" class="tab-pane" id="'+id+'">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. </div>')
      }
      else{
      return;
      }
      },
      remove_tab: function(type,value){
          var self = this;
          if(type !== "click") return;
      if (type == "click" || type==undefined){
        var self = this;
          var cycle = this.$inner.length;
          var $active_tab = this.$inner.find("div[class='tabpanel'].active");
          var $active_content=this.$indicators.find('li.active');
          $active_tab.remove();
          $active_content.remove();
      }
      else{
      return;
      }     
      },
      drop_and_build_snippet: function() {
          var self = this;
          this._super();
          this.id = "tab_slide_" + new Date().getTime();
          this.$target.attr("id", this.id);        
          this.add_tab().fail(function () {
              self.editor.on_remove();
          });
      },
    }); 

     options.registry.js_embed_html = options.Class.extend({
        /* start: function (editMode) {
            var self = this;
            this._super();          
        }, */
        edit_html: function(type,value) {
          var self = this;
          /*if(type !== "click") return;*/
          if (type == "click" || type==undefined){
            self.$modal = $(qweb.render("theme_impacto.edit_html_modal"));
            self.$modal.appendTo('body');
            self.$modal.modal();
            var $htmlvalue = self.$modal.find("#html_data"),
                $sub_data = self.$modal.find("#sub_data"); 
                $htmlvalue.val(self.$target.html());
                $sub_data.on('click', function() {
                  var html = $htmlvalue.val();
                  var live_str = $('<div>',{html:html});
                  var data = live_str.find('[data-html]');
                  var final = live_str;
                  if(data.length > 0){
                     var style = data.attr('style');
                     if(style)  self.$target.attr('style',style)
                      var cls = data.attr('class');
                      if(cls) self.$target.addClass(cls).attr('style',style);
                     var final = data.removeAttr('data-html').removeAttr('class').removeAttr('style');
                  } else {
                    
                  }
                  self.$target.empty().append(final);

                  var bar = live_str.find('.progress-bar');
                  if(bar.length > 0) IMPACTO.progressBar();

                 /* var rskill = live_str.find('.rounded-skill');
                  if(rskill.length > 0) IMPACTO.roundedSkill();*/

                  var counter = live_str.find('.counter');
                  if(counter.length > 0) IMPACTO.counters();

                  var counter = live_str.find('.isotope');
                  if(counter.length > 0) IMPACTO.Isotope();

                });              
             }
          else {
            return;
          }         
        },
        drop_and_build_snippet: function() {
            var self = this;
            this._super();       
            this.edit_html().fail(function () {
                self.editor.on_remove();
            });
        }
    });

   /* options.registry.js_rounded_skill = options.Class.extend({
        start: function () {
            var self = this;
            this._super();
        },
        clean_for_save: function () {
            var $self = this;
             $self.$target.removeAttr('style');
             $self.$target.removeClass('skills-animated');
             $self.$target.find('canvas').remove();
        },
        update_skill: function(type,value) {
          var self = this;
          if(type !== "click") return;
          if (type == "click" || type==undefined){
            self.$modal = $(qweb.render("theme_impacto.update_skill_modal"));
            self.$modal.appendTo('body');
            self.$modal.modal();
            var $chart_per = self.$modal.find("#chart_per"),
                $chart_color = self.$modal.find("#chart_color"),
                $sub_data = self.$modal.find("#sub_data"),
                $chart_width = self.$modal.find("#chart_width"),                
                $p_data = self.$target.attr('data-percent'),
                $c_data = self.$target.attr('data-color'),
                $w_data = self.$target.attr('data-width');
                $chart_per.val($p_data);
                $chart_color.val($c_data);
                $chart_width.val($w_data);

                $sub_data.on('click', function() {
                     var elm = self.$target;
                     elm.attr('data-percent',$chart_per.val());
                     elm.attr('data-color',$chart_color.val());                     
                     elm.attr('data-width',$chart_width.val());  
                });

             }
          else {
           return;
          }         
        },
        drop_and_build_snippet: function() {
            var self = this;
            this._super();       
            this.update_skill().fail(function () {
                self.editor.on_remove();
            });
        },
    });*/
    options.registry.js_progress_bar = options.Class.extend({
        start: function () {
            var self = this;
            this._super();
        },
        clean_for_save: function () {
            var $self = this;
            var no = $self.$target.find('.progress-number');
            var number = no.text();
            if(number != '' ) $self.$target.attr('data-percent',number);
             $self.$target.removeAttr('style');
             $self.$target.find('.progress-type').remove();
             no.remove();
        },        
    });

    options.registry.js_counter = options.Class.extend({
        start: function () {
            var self = this;
            this._super();
        },
        clean_for_save: function () {
            var $self = this;
            var count = $self.$target.find('.timer');
            var number = count.text();
            count.attr('data-to',number);
        },        
    });

    // js_get_posts
    options.registry.js_get_posts = options.Class.extend({
        drop_and_build_snippet: function () {
            if (!this.$target.data('snippet-view')) {
                this.$target.data("snippet-view", new animation.registry.js_get_posts(this.$target));
            }
        },

        clean_for_save: function () {
            this.$target.empty();
        },
    });

    // js_get_posts limit
    options.registry.js_get_posts_limit = options.Class.extend({
        start: function () {
            var self = this;
            setTimeout(function () {
                var ul = self.$overlay.find(".snippet-option-js_get_posts_limit > ul");
                if (self.$target.attr("data-posts_limit")) {
                    var limit = self.$target.attr("data-posts_limit");
                    ul.find('li[data-posts_limit="' + limit + '"]').addClass("active");
                } else {
                    ul.find('li[data-posts_limit="3"]').addClass("active");
                }
            }, 100)
        },

        posts_limit: function (type, value, $li) {
            var self = this;
            if (type != "click") {return}
            value = parseInt(value);
            this.$target.attr("data-posts_limit",value)
                                    .data("posts_limit",value)
                                    .data('snippet-view').redrow(true);
            setTimeout(function () {
                $li.parent().find("li").removeClass("active");
                $li.addClass("active");
            }, 100);
        },
    });

    // js_get_posts Select Blog
    options.registry.js_get_posts_selectBlog = options.Class.extend({
        start: function () {
            this._super();
            var self      = this;
            var model     = new Model('blog.blog');
            var blogsList = [];

            model
            .call('search_read',
            [
                [],
                ['name','id']// attributes to get
            ],
            {} )
            .then(function (blogs) {
                self.createBlogsList(blogs)// start printing posts...
            })
            .fail(function (e) {
                // No data
                var title = _t("Oops, Huston we have a problem"),
                    msg   = $("<div contenteditable='false' class='message error text-center'><h3>"+ title +"</h3><code>"+ e.data.message + "</code></div>" );
                self.$target.append(msg)
                return;
            });
        },

        createBlogsList: function (blogs) {
            var self = this;
            var ul = null;

            setTimeout(function () {
                ul = self.$overlay.find(".snippet-option-js_get_posts_selectBlog > ul");
                $(blogs).each(function () {
                    var blog = $(this);
                    var li = $('<li data-filter_by_blog_id="' + blog[0].id + '"><a>' + blog[0].name + '</a></li>');
                    ul.append(li);
                });
                if (self.$target.attr("data-filter_by_blog_id")) {
                    var id = self.$target.attr("data-filter_by_blog_id");
                    ul.find("li[data-filter_by_blog_id=" + id  + "]").addClass("active");
                }
            },100)
        },

        filter_by_blog_id: function (type, value, $li) {
            var self = this;
            if (type == "click") {
                $li.parent().find("li").removeClass("active");
                $li.addClass("active");
                value = parseInt(value);
                self.$target.attr("data-filter_by_blog_id",value)
                                        .data("filter_by_blog_id",value)
                                        .data('snippet-view').redrow(true);
            }
        },
    });

   

    return options;

});



