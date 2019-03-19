# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    bill_report = fields.Text("Vendor Bill Report",
                              default="- Documen ini berguna sebagai bukti proses pembayaran yang akan dilakukan oleh INNOGRAPH \n- Pembayaran akan di proses dengan kelengkapan sebagai berikut:\n   - Invoice \n   - Faktur Pajak \n   - Surat Penawaran \n   -Surat Jalan/BAST \n   - dan Bukti Penagihan lainnya \n- Termin Pembayaran dihitung sejak Invoice diterima")
    invoice_report = fields.Text("Customer Invoice Report",
                                 default="- Mohon Mencantumkan referensi No. Kwitansi / Invoice dan Nama Perusahaan di kolom berita formulir transfer \n- Please indicate the Invoice number and Company name in the message column on the transfer slip")
