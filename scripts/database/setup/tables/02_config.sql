CREATE TABLE config (
    config_id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    request_max_requests BIGINT NOT NULL,
    request_batch_size INTEGER NOT NULL,
    asession_max_concurrency_min INTEGER NOT NULL,
    asession_max_concurrency_max INTEGER NOT NULL,
    asession_retries INTEGER NOT NULL,
    asession_timeout INTEGER NOT NULL,
    throttle_request_rate FLOAT NOT NULL,
    throttle_burnin_period INTEGER NOT NULL,
    throttle_burnin_reset INTEGER NOT NULL,
    throttle_burnin_rate FLOAT NOT NULL,
    throttle_burnin_threshold_factor INTEGER NOT NULL,
    throttle_rolling_window_size INTEGER NOT NULL,
    throttle_cooldown_factor INTEGER NOT NULL,
    throttle_cooldown_phase INTEGER NOT NULL,
    throttle_tolerance FLOAT NOT NULL
);
