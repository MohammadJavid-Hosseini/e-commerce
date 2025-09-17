# todo, fixme, hack, note, bug, xxx
# NOTE: confirming an order process
#       1. customer adds goods to cart (creating cartItems)
#          when ready, customer orders (an order is created)
#       2. seller confirms the OrderItem (availibility checked),
#          or rejects it for any reason.
#       3. when admin tries to confirm the order, if all items are already \
#          confirmed, order's status changes to processing,
#          otherwise, to failed. admin, in turn, updates order explanation.
#       4. customer sees the status of order in its orders list,
#          if any order is rejected, chenges the quantity and tries again.
#          if the problem is not quantity and there's something wrong with \
#          the store, there is nothing that customer can do.

# FIXME: 1. OrderItem view: for OrderItem we need views for single and mass \
#           cofirmation/reject, only by the seller. stock checking happens \
#           here, yet seller can reject it manually for other reasons
#        2. Order view: single and mass confirmation for admin.


# FIXME: 1. create a Seller object; best_seller in ProductList API expects an object of Seller.