/**
 *    Copyright 2013 Matthieu Moquet
 *    Copyright 2016-2017 LasLabs Inc.
 *    License MIT (https://opensource.org/licenses/MIT)
 **/

odoo.define('cropper_image.widget', function(require) {
    'use strict';

    var core = require('web.core')
    var common = require('web.form_common')
    var session = require('web.session')
    var utils = require('web.utils')

    var QWeb = core.qweb

    var FieldCropperImage = common.AbstractField.extend(common.ReinitializeFieldMixin, {
        events: {
            'click .o_fieldcropper_save': '_on_click_save',
            'click .o_fieldcropper_change_image': '_on_click_change_image',
            'click .cropper-file-input': '_on_input_file_change',
        },
        className: 'croopper_image-widget',
        // template: 'FieldCropperImage',
        // placeholder: "/web/static/src/img/placeholder.png",
        // darkroom: null,
        // no_rerender: false,

        defaults: {

        },
        cropperOptions: {
            aspectRatio: 16 / 9,
        },

        init: function(field_manager, node) {
        	console.log("INIT")
            this._super(field_manager, node)
            this.options = _.defaults(this.options, this.defaults)

            var aspectRatio = eval(this.node.attrs.aspect_ratio)
            if (aspectRatio){
            	this.options.aspectRatio = aspectRatio
            }
            console.log("CALLED CROPPER JS INIT")
        },
        __fetch_image_url: function() {
            var field = this.name
            var url = null
            console.log("::::::::::::::::INIT CROPPER")
            if (this.get('value') && !utils.is_bin_size(this.get('value'))) {
                url = 'data:image/png;base64,' + this.get('value')
            } else if (this.get('value')) {
                var id = JSON.stringify(this.view.datarecord.id || null);
                var field = this.name
                if (this.options.preview_image) {
                    field = this.options.preview_image
                }

                url = session.url('/web/image', {
                    model: this.view.dataset.model,
                    id: id,
                    field: field,
                    unique: (this.view.datarecord.__last_update || '').replace(/[^0-9]/g, ''),
                });
            } else {
                url = this.placeholder
            }
            return url
        },
        _init_cropper: function() {
            var url = this.__fetch_image_url()
            this.$cropper_obj = $(QWeb.render("FieldCropperImage", {
                widget: this,
                url: url
            }))
            
            this.$cropper_obj.cropper(this.options)
            this.$el.find('> img').remove()

            this.$el.append(this.$cropper_obj)

            this._render_button()

        },

        _render_button: function() {
            var btn_bar = $(QWeb.render('FieldCropperImage-btn-bar', {
                widget: this
            }))
            this.$el.prepend(btn_bar)
        },

        destroy_content: function() {
            console.log("RUNNING destroy_content")
            this.$el.html('')
        },
        set_value: function(value) {
            return this._super(value)
        },

        _render_readonly: function() {
            var url = this.__fetch_image_url()
            this.$el.append($(QWeb.render('FieldCropperImage-readonly', {
                widget: this,
                url: url
            })))
        },
        render_value: function() {
            this.destroy_content()

            if (this.get("effective_readonly")) {
                this._render_readonly()
            } else {

                this._init_cropper()
            }
        },
        _on_input_file_change: function() {
        	var self = this
            var URL = window.URL || window.webkitURL
            var uploadedImageName = 'cropped.jpg'
			var uploadedImageType = 'image/jpeg'
			var uploadedImageURL

            var $inputImage = this.$el.find('.cropper-file-input')
            if (URL) {
            	var $image = this.$cropper_obj
                $inputImage.change(function() {
                    var files = this.files
                    var file

                    if (!$image.data('cropper')) {
                        return;
                    }

                    if (files && files.length) {
                        file = files[0]
                        if (/^image\/\w+$/.test(file.type)) {
                            uploadedImageName = file.name
                            uploadedImageType = file.type

                            if (uploadedImageURL) {
                                URL.revokeObjectURL(uploadedImageURL)
                            }

                            uploadedImageURL = URL.createObjectURL(file)
                            $image.cropper('destroy').attr('src', uploadedImageURL).cropper(self.options)
                            $inputImage.val('')
                        } else {
                            window.alert('Please choose an image file.')
                        }
                    }
                })
            }
        },

        _clear_input_file_elm: function(e) {
            this.$el.find('input[type="file"]').remove()
        },
        _add_input_file_elm: function(e) {
            this._clear_input_file_elm()
            this.$el.prepend('<input type="file" name="' + this.name + '" class="cropper-file-input hidden" accept="image/*" />')
        },
        _on_click_change_image: function(e) {
            // input file elm first
            this._add_input_file_elm()
                // then click it to show pop up file selection
            this.$el.find('input[type="file"]').click()
        },
        _on_click_save: function(e) {
            var self = this
            console.log("CLICKING BUTTON SAVE")
                // console.log(e)
                // console.log(this)

            // console.log(this.$cropper_obj)
            // console.log(this.$el.find('.cropper-img').getCropper)
            var $img = this.$cropper_obj
            var imageData = $img.cropper('getImageData')
            var croppedCanvas = $img.cropper('getCroppedCanvas')
            var blob = croppedCanvas.toDataURL('image/png')

            var raw_base64 = blob.split(',')[1]
            

            var rec_values = {}
            rec_values[this.node.attrs.name] = raw_base64
            return this.view.dataset._model.call(
                'write', [
                    [this.view.datarecord.id],
                    rec_values,
                    self.view.dataset.get_context()
                ]).done(function() {
                self.reload_record()
            })
        },
        commit_value: function(blob) {
            this.set_value(blob)
        },
        reload_record: function() {
            this.view.reload()
        },
    })

    core.form_widget_registry.add("cropper", FieldCropperImage)

    return {
        FieldCropperImage: FieldCropperImage
    }
})