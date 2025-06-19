-- Insert some availability data for the test vendors
-- Update availability data for the test vendors
UPDATE public.vendor_availability
SET status = 'available'
WHERE vendor_id = '64d89e91-c21e-4941-85c6-b03ed6d45b86' AND available_date = '2024-07-01';

UPDATE public.vendor_availability
SET status = 'booked_tentative'
WHERE vendor_id = '64d89e91-c21e-4941-85c6-b03ed6d45b86' AND available_date = '2024-07-02';

UPDATE public.vendor_availability
SET status = 'available'
WHERE vendor_id = '64d89e91-c21e-4941-85c6-b03ed6d45b86' AND available_date = '2024-07-03';

UPDATE public.vendor_availability
SET status = 'available'
WHERE vendor_id = 'd506933a-af60-4d6e-a168-1f319ba7e106' AND available_date = '2024-07-05';

UPDATE public.vendor_availability
SET status = 'unavailable_custom'
WHERE vendor_id = 'd506933a-af60-4d6e-a168-1f319ba7e106' AND available_date = '2024-07-06';
