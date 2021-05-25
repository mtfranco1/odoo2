# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import logging

from datetime import datetime, timedelta
from odoo import models, fields

_logger = logging.getLogger(__name__)


class CommonLogBookEpt(models.Model):
    """Inherit the common log book here to handel the log book in the connector"""
    _inherit = "common.log.book.ept"

    shopify_instance_id = fields.Many2one("shopify.instance.ept", "Instance")

    def create_crash_queue_schedule_activity(self, queue_id, model_id, note):
        """
        This method is used to create a schedule activity for the queue crash.
        Base on the Shopify configuration when any queue crash will create a schedule activity.
        :param queue_id: Record of the queue(customer,product and order)
        :param model_id: Record of model(customer,product and order)
        :param note: Message
        @author: Nilesh Parmar
        @author: Maulik Barad as created common method for all queues on dated 17-Feb-2020.
        Date: 07 February 2020.
        Task Id : 160579
        """
        mail_activity_obj = self.env['mail.activity']
        activity_type_id = queue_id and queue_id.shopify_instance_id.shopify_activity_type_id.id
        date_deadline = datetime.strftime(
            datetime.now() + timedelta(days=int(queue_id.shopify_instance_id.shopify_date_deadline)), "%Y-%m-%d")

        if queue_id:
            for user_id in queue_id.shopify_instance_id.shopify_user_ids:
                mail_activity = mail_activity_obj.search(
                    [('res_model_id', '=', model_id), ('user_id', '=', user_id.id), ('res_id', '=', queue_id.id),
                     ('activity_type_id', '=', activity_type_id)])
                if not mail_activity:
                    vals = self.prepare_vals_for_schedule_activity(activity_type_id, note, queue_id, user_id, model_id,
                                                                   date_deadline)
                    try:
                        mail_activity_obj.create(vals)
                    except:
                        _logger.info("Unable to create schedule activity, Please give proper "
                                     "access right of this user :%s  ", user_id.name)
        return True

    def prepare_vals_for_schedule_activity(self, activity_type_id, note, queue_id, user_id, model_id, date_deadline):
        """ This method used to prepare a vals for the schedule activity.
            :param activity_type_id: Record of the activity type(email,call,meeting, to do)
            :param user_id: Record of user(whom to assign schedule activity)
            :param date_deadline: date of schedule activity dead line.
            @return: values
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 14 October 2020 .
            Task_id: 167537
        """
        values = {'activity_type_id': activity_type_id,
                  'note': note,
                  'res_id': queue_id.id,
                  'user_id': user_id.id or self._uid,
                  'res_model_id': model_id,
                  'date_deadline': date_deadline
                  }
        return values

    def shopify_create_common_log_book(self, process_type, instance, model_id):
        """ This method used to create a log book record.
            :param type: Generally, the type value is 'import' or 'export'.
            :model_id: record of model.
            @return: log_book_id
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 16 October 2020 .
        """
        log_book_id = self.create({"type": process_type,
                                   "module": "shopify_ept",
                                   "shopify_instance_id": instance.id if instance else False,
                                   "model_id": model_id,
                                   "active": True})
        return log_book_id


class CommonLogLineEpt(models.Model):
    _inherit = "common.log.lines.ept"

    shopify_product_data_queue_line_id = fields.Many2one("shopify.product.data.queue.line.ept",
                                                         "Shopify Product Queue Line")
    shopify_order_data_queue_line_id = fields.Many2one("shopify.order.data.queue.line.ept",
                                                       "Shopify Order Queue Line")
    shopify_customer_data_queue_line_id = fields.Many2one("shopify.customer.data.queue.line.ept",
                                                          "Shopify Customer Queue Line")

    def shopify_create_product_log_line(self, message, model_id, queue_line_id, log_book_id, sku=""):
        """
        This method used to create a log line for product mismatch logs.
        @return: log_line
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 22/10/2019.
        @change: Maulik Barad on Date 02-Sep-2020.
        """
        vals = self.shopify_prepare_log_line_vals(message, model_id, queue_line_id, log_book_id)

        vals.update({
            'shopify_product_data_queue_line_id': queue_line_id.id if queue_line_id else False,
            "default_code": sku
        })
        log_line = self.create(vals)
        return log_line

    def shopify_create_order_log_line(self, message, model_id, queue_line_id, log_book_id, order_ref=""):
        """This method used to create a log line for order mismatch logs.
            @param : self, message, model_id, queue_line_id
            @return: log_line
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 11/11/2019.
        """
        if order_ref:
            domain = [("message", "=", message), ("model_id", "=", model_id), ("order_ref", "=", order_ref)]
            log_line = self.search(domain)
            if log_line:
                log_line.update({"write_date": datetime.now(), "log_book_id": log_book_id.id if log_book_id else False,
                                 "shopify_order_data_queue_line_id": queue_line_id and queue_line_id.id or False})
                return log_line

        vals = self.shopify_prepare_log_line_vals(message, model_id, queue_line_id, log_book_id)

        vals.update({'shopify_order_data_queue_line_id': queue_line_id and queue_line_id.id or False,
                     "order_ref": order_ref})
        log_line = self.create(vals)
        return log_line

    def shopify_create_customer_log_line(self, message, model_id, queue_line_id, log_book_id):
        """This method used to create a log line for customer mismatch logs.
        """
        vals = self.shopify_prepare_log_line_vals(message, model_id, queue_line_id, log_book_id)
        vals.update({
            'shopify_customer_data_queue_line_id': queue_line_id and queue_line_id.id or False,
        })
        log_line = self.create(vals)
        return log_line

    def shopify_prepare_log_line_vals(self, message, model_id, res_id, log_book_id):
        """ Prepare vals for the log line.
            :param message: Error/log message
            :param model_id: Record of model
            :param res_id: Res Id(Here we can set process record id).
            :param log_book_id: Record of log book.
            @return: vals
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 14 October 2020 .
            Task_id: 167537
        """
        vals = {'message': message,
                'model_id': model_id,
                'res_id': res_id.id if res_id else False,
                'log_book_id': log_book_id.id if log_book_id else False,
                }
        return vals
