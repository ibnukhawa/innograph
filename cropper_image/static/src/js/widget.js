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
	var _t = core._t

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
			this._super(field_manager, node)

			this.new_record = true
			if(this.view.datarecord.id){
				this.new_record = false
			}
			this.options = _.defaults(this.options, this.defaults)

			var aspectRatio = eval(this.node.attrs.aspect_ratio)
			if (aspectRatio) {
				this.options.aspectRatio = aspectRatio
			}

		},
		__fetch_image_url: function() {
			var field = this.name
			var url = null

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
			// this._add_input_file_elm()
				// then click it to show pop up file selection
			this.$el.find('input[type="file"]').click()
		},


		_get_blob_image: function() {
			var $img = this.$cropper_obj
			var imageData = $img.cropper('getImageData')
			var croppedCanvas = $img.cropper('getCroppedCanvas')
			var blob = croppedCanvas.toDataURL('image/png')
			return blob
		},

		set_filename: function(value) {
			var filename = this.node.attrs.filename;
			if (filename) {
				var field = this.field_manager.fields[filename];
				if (field) {
					field.set_value(value);
					field._dirty_flag = true;
				}
			}
		},
		_on_click_save: function(e) {
			var self = this

			var blob = this._get_blob_image()

			var raw_base64 = blob.split(',')[1]

			var rec_values = {}
			rec_values[this.node.attrs.name] = raw_base64

			if (!this.new_record) {
				return this.view.dataset._model.call(
					'write', [
						[this.view.datarecord.id],
						rec_values,
						self.view.dataset.get_context()
					]).done(function(res) {
						self.reload_record(res)
					})

			}else {
				// this._add_input_file_elm()
				var self = this
				return this.view.dataset._model.call(
					'create', [
						rec_values,
						self.view.dataset.get_context()
					]).
					done(function(res) {
						self.view.dataset._model.call('read',[
								[res],
								[]
							]).then(function(rec){
								self.reload_record(rec[0])
							})
					}
				)
			}



		},
		commit_value: function(blob) {
			this.set_value(blob)
		},
		reload_record: function(record) {
			// this.view.reload()
			// this.view.load_record(record)

			var action = {
	            type: 'ir.actions.act_window',
	            res_model: this.view.dataset.model,
	            view_mode: 'form',
	            view_type: 'form',
	            views: [[false, 'form']],
	            name: _t('Record'),
	            target: 'current',
	            res_id:record.id,
	            context: {
	                'default_res_model': this.view.dataset.model,
	                'default_res_id': record.id,
	            },
	        };
	        this.do_action(action, {
	            on_close: function () {
	                self.read_value();
	            },
	        });
		},
	})

	core.form_widget_registry.add("cropper", FieldCropperImage)

	return {
		FieldCropperImage: FieldCropperImage
	}
})